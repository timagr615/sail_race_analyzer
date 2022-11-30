from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

from .db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    username = Column(String, unique=True)
