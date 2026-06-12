import os
import threading
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserResponse, UserLogin
from app import crud
import jwt
from app.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
MAX_FAILED_ATTEMPTS = settings.MAX_FAILED_ATTEMPTS
LOCKOUT_DURATION_MINUTES = settings.LOCKOUT_DURATION_MINUTES

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Global lock to guarantee atomic read-modify-write operations on the in-memory dictionary
tracker_lock = threading.Lock()
FAILED_ATTEMPTS_TRACKER = {}

def create_access_token(data: dict):
    """
    Generate a secure JWT access token with an expiration timestamp.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_analyst(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new SOC analyst or admin using email validation.
    """
    # 🔄 Changed check from username to email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    return crud.create_user(db=db, user=user)

@router.post("/login", response_model=UserResponse)  # 🔄 Added response model to return user data
def login_analyst(user_credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate an analyst via email with Brute-Force protection and issue a secure JWT cookie.
    """
    # 🔄 Switched from username tracking to email tracking
    email = user_credentials.email
    current_time = datetime.now(timezone.utc)

    # Thread-Safe Lockout Evaluation
    with tracker_lock:
        user_track = FAILED_ATTEMPTS_TRACKER.get(email)

        if user_track and user_track["count"] >= MAX_FAILED_ATTEMPTS:
            locked_at = user_track.get("locked_at")
            
            if locked_at is None:
                locked_at = current_time
                user_track["locked_at"] = current_time

            if current_time - locked_at > timedelta(minutes=LOCKOUT_DURATION_MINUTES):
                del FAILED_ATTEMPTS_TRACKER[email]
            else:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Account is temporarily locked due to too many failed attempts. Please try again later."
                )

    # 2. Fetch the user from the database via Email 🔄
    db_user = crud.get_user_by_email(db, email=email)
    
    # 3. Verify existence and validate password securely using bcrypt
    if not db_user or not crud.verify_password(user_credentials.password, db_user.password_hash):
        with tracker_lock:
            if email not in FAILED_ATTEMPTS_TRACKER:
                FAILED_ATTEMPTS_TRACKER[email] = {"count": 1, "locked_at": None}
            else:
                FAILED_ATTEMPTS_TRACKER[email]["count"] += 1
                if FAILED_ATTEMPTS_TRACKER[email]["count"] >= MAX_FAILED_ATTEMPTS:
                    FAILED_ATTEMPTS_TRACKER[email]["locked_at"] = current_time

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
        
    # 🔒 Defensive check: Block inactive accounts immediately during login
    if db_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your account is currently disabled."
        )
    
    # 4. Success! Clear the tracker completely for this user
    with tracker_lock:
        if email in FAILED_ATTEMPTS_TRACKER:
            del FAILED_ATTEMPTS_TRACKER[email]
    
    # 5. Generate Token and set the secure HttpOnly cookie (Mapping email in payload) 🔄
    token_data = {"id": db_user.id, "email": db_user.email}
    access_token = create_access_token(data=token_data)
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    # Returning the full user object to synch up frontend state immediately
    return db_user