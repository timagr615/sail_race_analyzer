from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users.user import User

from sqlalchemy.exc import IntegrityError

from app.models.db import get_session
from app.schemas.users.user import UserSch


async def get_all_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User))
    return result.scalars()


async def create_user(session: AsyncSession, user: UserSch) -> User:
    new_user = User(**user.dict())
    session.add(new_user)
    try:
        await session.commit()
        return new_user
    except IntegrityError as ex:
        await session.rollback()
        raise ValueError("The user is already excist")