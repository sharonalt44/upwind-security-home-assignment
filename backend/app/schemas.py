from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr
from typing import List, Literal, Optional

# Strict type definitions to enforce valid application boundaries
AllowedRole = Literal["admin", "analyst", "viewer"]
AllowedStatus = Literal["active", "disabled"]
AllowedSeverity = Literal["low", "medium", "high", "critical", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
EventStatus = Literal["Open", "In Progress", "Resolved"]


class UserBase(BaseModel):
    """
    Base schema containing shared user validation attributes.
    Utilizes EmailStr to guarantee incoming input strictly adheres to RFC email standards.
    """
    email: EmailStr


class UserCreate(UserBase):
    """
    Input validation schema for registering new user accounts.
    Enforces a strict minimum password length constraint to mitigate weak credential vulnerabilities.
    """
    password: str = Field(min_length=8, description="Minimum 8 characters required.")
    role: AllowedRole = "analyst"
    status: AllowedStatus = "active"


class UserResponse(UserBase):
    """
    Data Transfer Object (DTO) for outgoing user payloads.
    Safely sanitizes system responses by ensuring the plaintext password_hash is never leaked.
    """
    id: str
    role: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    Validation schema used to modify user state attributes via administrative operations.
    """
    status: Optional[AllowedStatus] = None
    role: Optional[AllowedRole] = None


class UserLogin(BaseModel):
    """
    Strict validation structure capturing incoming authentication credentials.
    """
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    """
    Core validation schema for security incidents.
    Implements Pydantic string constraints (constr) to prevent empty fields or arbitrary 
    long payloads, acting as an active barrier against script injections and buffer manipulation.
    """
    id: str
    severity: AllowedSeverity
    title: constr(min_length=3, max_length=100)
    asset: constr(min_length=1, max_length=100)
    source_ip: str
    timestamp: str
    user_id: str


class EventCreate(EventBase):
    """
    Schema handling incoming security event generation requests.
    """
    tags: Optional[List[str]] = None


class EventUpdate(BaseModel):
    """
    Validation gatekeeper for updating security incidents.
    Replaces loose string fields with explicit constraints to sanitize patch payloads.
    """
    status: Optional[EventStatus] = None
    comments: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list)
    severity: Optional[AllowedSeverity] = None
    user_id: Optional[str] = None
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    asset: Optional[str] = Field(None, min_length=1, max_length=100)
    source_ip: Optional[str] = Field(None, min_length=7, max_length=45)


class EventResponse(EventBase):
    """
    Secure serialization class formatting outgoing data packages for the frontend UI.
    """
    description: Optional[str] = ""
    status: Optional[str] = "Open"
    comments: Optional[str] = ""
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)