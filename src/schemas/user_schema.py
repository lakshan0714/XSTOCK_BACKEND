from typing import Optional
from pydantic import BaseModel, EmailStr
import enum


class UserRole(enum.Enum):
    admin = "admin"
    superadmin ="superadmin"



class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole  # Must be one of 'creater', 'merchandiser', 'user'



class Userlogin(BaseModel):
    email: EmailStr
    password: str
   

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None  # or Optional[UserRole] if using enum
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Schema for changing user password."""
    old_password: str
    new_password: str
    
    class Config:
        from_attributes = True


class AdminPasswordChange(BaseModel):
    """Schema for admin to change any user's password."""
    new_password: str
    
    class Config:
        from_attributes = True
