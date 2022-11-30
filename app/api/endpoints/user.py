from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.user import User
from app.schemas.users.user import UserSch
from app.crud.users.user import get_all_users, create_user
from app.models.db import get_session


router = APIRouter()


@router.get('/list', response_model=list[UserSch])
async def read_users(db_session: AsyncSession = Depends(get_session)):
    users = await get_all_users(db_session)
    return [UserSch(username=u.username, password=u.password, email=u.email) for u in users]


@router.post('/create', response_model=UserSch)
async def read_users(user: UserSch, db_session: AsyncSession = Depends(get_session)):
    user = await create_user(db_session, user)
    return UserSch(username=user.username, password=user.password, email=user.email)
