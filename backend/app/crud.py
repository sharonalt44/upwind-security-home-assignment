import time
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
import bcrypt

def get_user_by_email(db: Session, email: str):
    """Fetches a single user record from the DB matching the validated email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate, user_id: str = None):
    """
    Creates a new persistent User record.
    Accepts an optional user_id to support React-side generated IDs (e.g., String(Date.now())).
    """
    password_bytes = user.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    final_id = user_id if user_id else str(int(time.time() * 1000))
    
    # Map the Pydantic data to the SQLAlchemy model
    db_user = User(
        id=final_id,
        email=user.email,  
        password_hash=hashed_password,
        role=user.role,
        status=user.status if user.status else "active"  
    )
    
    # Save into the SQLite database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its stored bcrypt hash.
    The salt is automatically extracted from the hashed_password string.
    """
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    # Securely check if the plain password matches the cryptographic hash
    return bcrypt.checkpw(plain_bytes, hashed_bytes)