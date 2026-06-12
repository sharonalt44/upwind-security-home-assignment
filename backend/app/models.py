from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    
    password_hash = Column(String, nullable=False)
    
    # Roles allowed by frontend: "admin", "analyst", "viewer"
    role = Column(String, default="analyst", nullable=False) 
    
    # Statuses allowed by frontend: "active", "disabled"
    status = Column(String, default="active", nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)