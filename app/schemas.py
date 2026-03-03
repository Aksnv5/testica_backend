import datetime

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: Optional[str]
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: Optional[str]
    email: EmailStr
    is_active: bool
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginSchema(BaseModel):
    email: EmailStr
    password: str
