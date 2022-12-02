from sqlalchemy import update as sa_update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


class Model:
    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        session.add(cls(**kwargs))
        await session.commit()

    @classmethod
    async def update_by_id(cls, session: AsyncSession, id: int, **kwargs):
        query = sa_update(cls).where(cls.id == id).values(**kwargs).execution_options(synchronize_session="fetch")
        result = await session.execute(query)
        await session.commit()
        return result

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id: int):
        query = select(cls).where(cls.id == id)
        result = await session.execute(query)
        return result.one()
