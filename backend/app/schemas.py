from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from typing import List

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

    class Config:
        # Allows Pydantic to read data even if it comes as an object/attributes
        from_attributes = True