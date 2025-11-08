from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    name: Optional[str] = None
    surname: Optional[str] = None

class UserOut(BaseModel):
    email: EmailStr
    username: str
    name: Optional[str]
    surname: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
