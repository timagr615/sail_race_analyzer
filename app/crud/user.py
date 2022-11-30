from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

from sqlalchemy.exc import IntegrityError


async def get_all_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User))
    return result.scalars()


async def create_user(session: AsyncSession, username: str) -> User:
    new_user = User(username=username)
    session.add(new_user)
    try:
        await session.commit()
        return new_user
    except IntegrityError as ex:
        await session.rollback()
        raise ValueError("The user is already excist")