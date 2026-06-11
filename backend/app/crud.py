from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
import bcrypt

# 1. Check if a user already exists in the database by their username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# 2. Create a new SOC user in the DB with a securely hashed password
def create_user(db: Session, user: UserCreate):
    # Securely hash the plain text password using bcrypt
    password_bytes = user.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    # Map the Pydantic data to the SQLAlchemy model
    db_user = User(
        username=user.username,
        password_hash=hashed_password,
        role=user.role,
        status="approved"  # Automatically approved for now
    )
    
    # Save into the SQLite database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Refresh to capture the newly generated auto-increment ID
    
    return db_user