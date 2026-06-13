from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional
from typing import List

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "analyst"
    status: Optional[str] = "active"

class UserResponse(UserBase):
    id: str
    role: str
    status: str

    # Updated modern configuration style for Pydantic V2
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    status: Optional[str] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    # Updated modern configuration style for Pydantic V2
    model_config = ConfigDict(from_attributes=True)


# Core layout shared across all event models
class EventBase(BaseModel):
    id: str
    severity: str
    title: str
    asset: str
    source_ip: str
    timestamp: str
    user_id: str

# Schema for HTTP POST data ingestion (Admin only)
class EventCreate(EventBase):
    pass

# Schema for HTTP PATCH dynamic modification rules (Strictly controlled input fields)
class EventUpdate(BaseModel):
    status: Optional[str] = None
    comments: Optional[str] = None
    tags: Optional[List[str]] = None
    severity: Optional[str] = None  # Blocked in router logic if user is not Admin
    user_id: Optional[str] = None   # Blocked in router logic if user is not Admin
    title: Optional[str] = None     # Blocked in router logic if user is not Admin
    asset: Optional[str] = None     # Blocked in router logic if user is not Admin
    source_ip: Optional[str] = None # Blocked in router logic if user is not Admin

# Schema for JSON responses returned to the client
class EventResponse(EventBase):
    description: Optional[str] = ""
    status: Optional[str] = "Open"
    comments: Optional[str] = ""

    # Enable SQLAlchemy model compatibility
    class Config:
        from_attributes = True