import jwt
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app import crud
from app.models import User

def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Global authentication dependency middleware.
    Extracts the JWT from the secure HttpOnly cookie, validates its cryptographic signature,
    verifies session status against the token blacklist, and ensures the user account is active.
    """
    # 1. Extract the secure session token from incoming request cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Access token missing."
        )
    
    # 2. Cryptographic Session Revocation Check (Token Blacklist)
    # Validates that the user has not explicitly invalidated this session via logout
    is_blacklisted = crud.is_token_blacklisted(db, token=token)
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session revoked. Please login again."
        )
    
    try:
        # 3. Decode and verify the cryptographic integrity of the token payload
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
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
    
    # 4. Fetch the persistent user record via Email to ensure existence
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )
        
    # 5. Defensive Guard: Enforce strict account state access controls
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. User account is disabled or inactive."
        )
        
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Role-Based Access Control (RBAC) dependency.
    Validates that the authenticated session holder possesses explicit administrative 
    privileges before granting routing access to administrative payloads.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


def verify_user_ownership_or_admin(request: Request, current_user: User = Depends(get_current_user)):
    """
    Anti-BOLA / IDOR (Broken Object Level Authorization) validation dependency.
    Extracts the resource target identifier directly from the URL path parameters 
    and guarantees that non-admin analysts can exclusively access or modify their own data.
    """
    requested_user_id = request.path_params.get("user_id")
    
    if requested_user_id:
        requested_user_id = str(requested_user_id)

        if current_user.role != "admin" and str(current_user.id) != requested_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You cannot view or modify another user's resource."
            )
            
    return current_user