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
from app.saildata.schemas import SailDataDB, SailDataUpload, SailDataUpdate
from app.core.db import get_session

if TYPE_CHECKING:
    from app.users.models import User

S = TypeVar("S", bound='SailData')


class SailData(Base):
    __tablename__ = 'saildata'
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sail_boat: str = Column(String(20), nullable=True)
    wind_speed: str = Column(String(20), nullable=True)
    description: str = Column(String, nullable=True)
    notes: str = Column(String, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    user_id: int = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    user = relationship('User', back_populates='saildata', lazy='selectin')

    def __repr__(self):
        rep = f'Sail Data Model: {self.sail_boat}, {self.wind_speed}, {self.description}, ' \
              f'{self.notes}, {self.created_at}, {self.file_path}, {self.file_size} {self.user}'
        return rep

    @classmethod
    async def create(cls: Type[S], session: AsyncSession, data: SailDataUpload) -> S:
        datafile = cls(**data.dict())
        session.add(datafile)
        await session.commit()
        # print(datafile)
        return datafile

    @classmethod
    async def get_all(cls: Type[S], session: AsyncSession, limit: int = 100, offset: int = 0) -> list[S]:
        data = await session.execute(select(cls).offset(offset).limit(limit))
        return data.scalars().all()

    @classmethod
    async def get_by_id(cls: Type[S], session: AsyncSession, data_id: int) -> S:
        query = select(cls).where(cls.id == data_id)
        data = await session.execute(query)
        return data.scalars().first()

    @classmethod
    async def get_by_path(cls: Type[S], session: AsyncSession, path: str) -> S:
        query = select(cls).where(cls.file_path == path)
        data = await session.execute(query)
        return data.scalars().first()

    @classmethod
    async def get_by_user(cls: Type[S], session: AsyncSession, user_id: int) -> S:
        query = select(cls).where(cls.user_id == user_id)
        data = await session.execute(query)
        return data.scalars().all()

    @classmethod
    async def get_user_file(cls: Type[S], session: AsyncSession, user_id: int, data_id: int) -> S:
        query = select(cls).where(cls.user_id == user_id).where(cls.id == data_id)
        data = await session.execute(query)
        return data.scalars().first()

    @classmethod
    async def delete_by_id(cls: Type[S], session: AsyncSession, data_id: int) -> S:
        query = delete(cls).where(cls.id == data_id).returning(cls.file_path)
        data = await session.execute(query)
        await session.commit()
        return data.scalars().first()

    @classmethod
    async def update(cls: Type[S], session: AsyncSession, data: SailDataUpdate) -> bool:
        data_d = data.dict()
        data_d['updated_at'] = datetime.utcnow()
        query = sa_update(cls).where(cls.id == data.id).values(**data_d) \
            .execution_options(synchronize_session="fetch")
        result = await session.execute(query)
        await session.commit()
        return True

    @classmethod
    async def update_file_size(cls: Type[S], session: AsyncSession, size: int, path: str) -> bool:
        data_d = {'file_size': size, 'updated_at': datetime.utcnow()}
        file = await cls.get_by_path(session, path)
        query = sa_update(cls).where(cls.id == file.id).values(**data_d) \
            .execution_options(synchronize_session="fetch")
        result = await session.execute(query)
        await session.commit()
        return True
