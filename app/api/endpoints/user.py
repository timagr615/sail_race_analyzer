from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserSch
from app.crud.user import get_all_users, create_user
from app.models.db import get_session


router = APIRouter()


@router.get('/list', response_model=list[UserSch])
async def read_users(db_session: AsyncSession = Depends(get_session)):
    users = await get_all_users(db_session)
    return [UserSch(username=u.username) for u in users]


@router.get('/create', response_model=UserSch)
async def read_users(name: str, db_session: AsyncSession = Depends(get_session)):
    user = await create_user(db_session, name)
    return UserSch(username=user.username)
