from datetime import datetime
from enum import Enum
from pydantic import BaseModel, constr, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=2, max_length=50)


class UserCreate(UserBase):
    password: str
    firstname: str | None
    lastname: str | None
    country: str | None


class UserUpdateMe(BaseModel):
    username: constr(min_length=2, max_length=50)
    firstname: str | None
    lastname: str | None
    country: str | None


class UserUpdate(UserUpdateMe):
    id: int


class UserDisplay(UserBase):
    id: int
    verified: bool = False
    is_active: bool = True
    firstname: str | None
    lastname: str | None
    country: str | None

    class Config:
        orm_mode = True


class UserDisplayFull(UserDisplay):
    role: str = 'guest'
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        orm_mode = True
