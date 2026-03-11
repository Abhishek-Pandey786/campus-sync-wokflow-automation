"""
User Pydantic Schemas
Request/Response models for user operations
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

from db.models import UserRole


# Base User Schema
class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=100)


# User Creation Schema
class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.STUDENT
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
    
    @validator('username', pre=True, always=True)
    def generate_username(cls, v, values):
        """Auto-generate username from email if not provided"""
        if v is None and 'email' in values:
            return values['email'].split('@')[0]
        return v


# User Login Schema
class UserLogin(BaseModel):
    """Schema for user login"""
    username: str  # Can be email or username
    password: str


# User Response Schema
class UserResponse(UserBase):
    """Schema for user response (no password)"""
    id: int
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


# Token Schema
class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Token Payload Schema
class TokenPayload(BaseModel):
    """Schema for JWT token payload"""
    sub: int  # user_id
    role: str
    exp: Optional[int] = None


# User Update Schema
class UserUpdate(BaseModel):
    """Schema for user profile update"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None


# Change Password Schema
class ChangePassword(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
