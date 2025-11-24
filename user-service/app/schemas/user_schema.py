from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    # Role id (integer) referencing roles table
    role_id: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    role_id: Optional[int] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role_id: Optional[int] = None
    role: Optional[str] = None

class TokenData(BaseModel):
    email: Optional[str] = None

class HealthCheck(BaseModel):
    status: str
    message: str
    timestamp: datetime

class RoleResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
