from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str  # Requis uniquement à la création

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)