from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[UUID] = None

class UserBase(BaseModel):
    email: str
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: Optional[str] = "user"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: UUID
    google_id: Optional[str] = None
    picture: Optional[str] = None
    is_active: bool
    is_superuser: Optional[bool] = False
    email_verified: Optional[bool] = False
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    code: str

class GoogleCallbackResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
