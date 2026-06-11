import os
import threading
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserResponse, UserLogin
from app import crud
import jwt

# Secure Secret Management: Read from environment or fallback to a dev key (Never hardcode in production)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_PENGUWAVE_KEY_FOR_SOC_PORTAL")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Global lock to guarantee atomic read-modify-write operations on the in-memory dictionary
tracker_lock = threading.Lock()

FAILED_ATTEMPTS_TRACKER = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

def create_access_token(data: dict):
    """
    Generate a secure JWT access token with an expiration timestamp.
    """
    to_encode = data.copy()
    # Fixed deprecation warning: using timezone-aware UTC datetime
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # PyJWT converts datetime objects automatically, but using timestamp is standard practice
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_analyst(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new SOC analyst or admin.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        # Note: In ultra-secure envs, this error message might be generic to prevent enumeration.
        # For this assignment, we explicitly inform the user.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )
    return crud.create_user(db=db, user=user)

@router.post("/login")
def login_analyst(user_credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate an analyst with Brute-Force protection and issue a secure JWT cookie.
    """
    username = user_credentials.username
    current_time = datetime.now(timezone.utc)

    # Thread-Safe Lockout Evaluation
    with tracker_lock:
        user_track = FAILED_ATTEMPTS_TRACKER.get(username)

        if user_track and user_track["count"] >= MAX_FAILED_ATTEMPTS:
            locked_at = user_track.get("locked_at")
            
            # Defensive guard: if locked_at is corrupt/None, default to current time
            if locked_at is None:
                locked_at = current_time
                user_track["locked_at"] = current_time

            if current_time - locked_at > timedelta(minutes=LOCKOUT_DURATION_MINUTES):
                del FAILED_ATTEMPTS_TRACKER[username]
            else:
                remaining_time = timedelta(minutes=LOCKOUT_DURATION_MINUTES) - (current_time - locked_at)
                minutes_left = int(remaining_time.total_seconds() // 60) + 1
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Account is temporarily locked. Try again in {minutes_left} minutes."
                )

    # 2. Fetch the user from the database
    db_user = crud.get_user_by_username(db, username=username)
    
    # 3. Verify existence and validate password securely using bcrypt
    if not db_user or not crud.verify_password(user_credentials.password, db_user.password_hash):
        with tracker_lock:
            if username not in FAILED_ATTEMPTS_TRACKER:
                FAILED_ATTEMPTS_TRACKER[username] = {"count": 1, "locked_at": None}
            else:
                FAILED_ATTEMPTS_TRACKER[username]["count"] += 1
                if FAILED_ATTEMPTS_TRACKER[username]["count"] >= MAX_FAILED_ATTEMPTS:
                    FAILED_ATTEMPTS_TRACKER[username]["locked_at"] = current_time

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
    
    # 4. Success! Clear the tracker completely for this user
    with tracker_lock:
        if username in FAILED_ATTEMPTS_TRACKER:
            del FAILED_ATTEMPTS_TRACKER[username]
    
    # 5. Generate Token and set the secure HttpOnly cookie
    token_data = {"user_id": db_user.id, "username": db_user.username}
    access_token = create_access_token(data=token_data)
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return {"message": "Login successful"}