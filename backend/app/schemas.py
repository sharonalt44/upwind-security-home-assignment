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

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    # Updated modern configuration style for Pydantic V2
    model_config = ConfigDict(from_attributes=True)


class EventResponse(BaseModel):
    id: str
    timestamp: str
    severity: str
    title: str
    description: str
    assetHostname: str  
    assetIp: str
    sourceIp: str
    tags: List[str]
    userId: str

    model_config = ConfigDict(from_attributes=True)