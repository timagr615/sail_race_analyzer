from typing import Type, TypeVar, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy import update as sa_update
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.core.config import settings
# from app.users.hashing import get_hashed_password, verify_password
# from app.users.schemas import UserCreate, UserDisplay, UserUpdate
from app.news.schemas import NewsCreate, NewsUpdate
if TYPE_CHECKING:
    from app.users.models import User

N = TypeVar('N', bound='News')


class News(Base):
    __tablename__ = 'news'
    id: int = Column(Integer, primary_key=True)
    title: str = Column(String(150), nullable=False)
    description: str = Column(String(250), nullable=True)
    text: str = Column(String, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow)
    user_id: int = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    user = relationship('User', back_populates='news', lazy='selectin')

    @classmethod
    async def create_news(cls: Type[N], session: AsyncSession, user_id: int, news: NewsCreate) -> N:
        new_news = cls(**news.dict(), user_id=user_id)
        session.add(new_news)
        await session.commit()
        return new_news

    @classmethod
    async def update_news(cls: Type[N], session: AsyncSession, news: NewsUpdate) -> N:
        news_d = news.dict()
        news_d['updated_at'] = datetime.utcnow()
        query = sa_update(cls).where(cls.id == news.id).values(**news.dict()) \
            .execution_options(synchronize_session="fetch")
        result = await session.execute(query)
        await session.commit()
        return result.scalars().all()

    @classmethod
    async def get_all(cls: Type[N], session: AsyncSession, offset: int = 0, limit: int = 100) -> list[N]:
        news = await session.execute(select(cls).offset(offset).limit(limit))
        return news.scalars().all()

    @classmethod
    async def get_by_id(cls: Type[N], session: AsyncSession, news_id: int) -> N:
        query = select(cls).where(cls.id == news_id)
        news = await session.execute(query)
        return news.scalars().first()

    @classmethod
    async def delete_by_id(cls: Type[N], session: AsyncSession, news_id: int) -> bool:
        query = delete(cls).where(cls.id == news_id)
        await session.execute(query)
        await session.commit()
        return True
