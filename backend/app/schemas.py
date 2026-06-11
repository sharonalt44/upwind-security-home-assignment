from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "analyst"

class UserResponse(UserBase):
    id: int
    role: str
    status: str

    # Updated modern configuration style for Pydantic V2
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str
    password: str

    # Updated modern configuration style for Pydantic V2
    model_config = ConfigDict(from_attributes=True)