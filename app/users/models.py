from typing import Type, TypeVar, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy import update as sa_update
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.core.config import settings
from app.users.hashing import get_hashed_password, verify_password
from app.users.schemas import UserCreate, UserDisplay, UserUpdate
if TYPE_CHECKING:
    from app.news.models import News
    from app.saildata.models import SailData

import asyncio
from app.core.db import get_session

T = TypeVar('T', bound='User')


class User(Base):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email: str = Column(String, nullable=False, unique=True)
    password: str = Column(String(255), nullable=False)
    username: str = Column(String(50), nullable=False)
    firstname: str = Column(String, nullable=True)
    lastname: str = Column(String, nullable=True)
    country: str = Column(String, nullable=True)

    verified: bool = Column(Boolean, default=False)
    is_active: bool = Column(Boolean, default=True)
    role: str = Column(String(100), default='guest')

    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="user", lazy='selectin')
    saildata = relationship("SailData", back_populates="user", lazy='selectin')

    # is_admin: bool = Column(Boolean, default=False)
    # is_superuser: bool = Column(Boolean, default=False)

    def __repr__(self):
        return f'USER: {self.username} {self.email} {self.password} {self.firstname} {self.lastname}'

    def check_password(self, password: str) -> bool:
        return verify_password(self.password, password)

    @classmethod
    async def verify_email_exist(cls: Type[T], session: AsyncSession, email: str) -> T | None:
        query = select(cls).where(cls.email == email)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def user_registration(cls: Type[T], session: AsyncSession, user: UserCreate) -> T:
        user.password = get_hashed_password(user.password)
        new_instance = cls(**user.dict(), news=[], saildata=[])
        session.add(new_instance)
        await session.commit()
        return new_instance

    @classmethod
    async def user_update(cls: Type[T], session: AsyncSession, user: UserUpdate) -> None:
        query = sa_update(cls).where(cls.id == user.id).values(**user.dict())\
            .execution_options(synchronize_session="fetch")
        await session.execute(query)
        await session.commit()

    @classmethod
    async def update_admin_role(cls: Type[T], session: AsyncSession, user: T) -> None:
        query = sa_update(cls).where(cls.email == user.email).values({'role': 'admin'}) \
            .execution_options(synchronize_session="fetch")
        await session.execute(query)
        await session.commit()

    @classmethod
    async def get_all(cls: Type[T], session: AsyncSession, limit: int = 100, offset: int = 0) -> list[T]:
        query = select(cls).offset(offset).limit(limit)
        users = await session.execute(query)
        return users.scalars().all()

    @classmethod
    async def get_by_id(cls: Type[T], session: AsyncSession, id: int) -> T:
        query = select(cls).where(cls.id == id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def delete_by_id(cls: Type[T], session: AsyncSession, id: int) -> bool:
        query = delete(cls).where(cls.id == id)
        await session.execute(query)
        await session.commit()
        return True

    @classmethod
    async def create_superuser(cls: Type[T], session: AsyncSession) -> None:
        user = cls(
            email=settings.admin_email,
            username=settings.admin_username,
            password=get_hashed_password(settings.admin_password),
            firstname=settings.admin_firstname,
            lastname=settings.admin_lastname,
            role='superuser',
            country='Russian Federation',
            news=[],
            saildata=[]
        )
        superuser_exist = await cls.verify_email_exist(session, settings.admin_email)
        if superuser_exist:
            return
        session.add(user)
        await session.commit()
