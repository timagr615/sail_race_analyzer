from datetime import datetime
from enum import Enum
from pydantic import BaseModel, constr


class NewsBase(BaseModel):
    title: str
    description: str | None
    text: str


class NewsCreate(NewsBase):
    pass


class NewsUpdate(NewsBase):
    id: int


class NewsDB(NewsBase):
    id: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    user_id: int

    class Config:
        orm_mode = True
