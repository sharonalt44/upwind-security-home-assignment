from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import bcrypt
import uuid

from app.models import User, BlacklistedToken
from app.schemas import UserCreate

def get_user_by_email(db: Session, email: str):
    """
    Resolves a single user profile targeting their unique email string.
    🛡️ Soft Delete Enforcement: Explicitly excludes accounts marked as removed.
    """
    return db.query(User).filter(
        User.email == email, 
        User.deleted_at.is_(None)
    ).first()


def get_user_by_id(db: Session, user_id: str):
    """
    Resolves a single user profile by their global unique identifier.
    🛡️ Soft Delete Enforcement: Filters out records containing a deletion timestamp.
    """
    return db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()


def get_all_users(db: Session):
    """
    Retrieves the entire active user directory list.
    🛡️ Soft Delete Enforcement: Automatically screens out deleted profiles from database dumps.
    """
    return db.query(User).filter(User.deleted_at.is_(None)).all()


def hash_password(plain_password: str) -> str:
    """
    Computes a secure cryptographic hash using the computational heavy bcrypt algorithm.
    Automatically generates a high-entropy salt block.
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def create_user(db: Session, user: UserCreate, user_id: str = None):
    """
    Creates a new user or modernizes/reactivates an existing soft-deleted profile 
    to resolve unique constraint conflicts on the email field.
    """
    # 1. Check if the email exists globally in the DB (ignoring the Soft Delete filter)
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        # If the user exists but is NOT soft-deleted, block it normally
        if existing_user.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database conflict: Email already registered and active."
            )
        
        # If the user was soft-deleted, resurrect the profile
        hashed_password = hash_password(user.password)
        existing_user.password_hash = hashed_password
        existing_user.role = user.role
        existing_user.status = user.status if user.status else "active"
        existing_user.deleted_at = None  # Clear the deletion timestamp to bring them back
        
        db.commit()
        db.refresh(existing_user)
        return existing_user

    # 2. Standard Flow: If the email never existed, compile a fresh unique profile
    hashed_password = hash_password(user.password)
    final_id = user_id if user_id else str(uuid.uuid4())

    db_user = User(
        id=final_id,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        status=user.status if user.status else "active"
    )

    db.add(db_user)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback() 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database conflict: Email already registered."
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares raw credential input bytes against an authentic password hash string.
    Maintains resistance against dynamic evaluation timing variations.
    """
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def blacklist_token(db: Session, token: str):
    """
    Revokes an active JSON Web Token signature on demand upon logout.
    Ensures state validation captures explicit termination sessions immediately.
    """
    db_token = BlacklistedToken(token=token)
    db.add(db_token)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        pass


def is_token_blacklisted(db: Session, token: str) -> bool:
    """
    Checks incoming user token sequences against the active blacklisted block collection.
    """
    if not token:
        return False
    return db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None