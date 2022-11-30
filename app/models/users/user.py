from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from app.models.db import Base


class User(Base):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String, nullable=False, unique=True)
    password: str = Column(String, nullable=False)
    username: str = Column(String, nullable=False, unique=True)
    verified: bool = Column(Boolean, default=False)
    is_admin: bool = Column(Boolean, default=False)
    is_superuser: bool = Column(Boolean, default=False)
    is_active: bool = Column(Boolean, default=False)
    firstname: str = Column(String, nullable=True)
    lastname: str = Column(String, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow)
