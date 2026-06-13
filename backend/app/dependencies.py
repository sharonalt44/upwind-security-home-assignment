import jwt
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app import crud
from app.models import User

def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Global authentication dependency.
    Extracts the JWT from the secure HttpOnly cookie, validates it,
    and returns the current authenticated user from the database.
    Now fully aligned with the email-based frontend schema.
    """
    # 1. Extract the secure token from incoming request cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Access token missing."
        )
    
    try:
        # 2. Decode and verify the cryptographic signature of the token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # 🔄 Changed from username to email to align with the frontend configuration
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: Email missing."
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please login again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token."
        )
    
    # 3. Ensure the user still exists in the database (Searching via Email)
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )
        
    # 4. Defensive guard: enforce account status access control
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. User account is disabled or inactive."
        )
        
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    RBAC Dependency: Validates that the authenticated session holder
    possesses administrative privileges before granting access.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user