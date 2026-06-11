from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 1. Schema defining what we expect to receive during registration (Register)
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username for the SOC member")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")
    role: Optional[str] = Field("analyst", description="The role in the SOC: 'analyst' or 'admin'")

# 2. Schema defining what data will be returned to the frontend/interviewer (without the password!)
class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    status: str
    created_at: datetime

    # Pydantic configuration to allow seamless data mapping from SQLAlchemy models (DB)
    class Config:
        from_attributes = True