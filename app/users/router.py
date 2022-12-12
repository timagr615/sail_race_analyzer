from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.schemas import UserDisplay, UserCreate, UserUpdate, UserUpdateMe, UserDisplayFull
from app.core.db import get_session
from app.users.models import User
from app.auth.jwt import get_current_user

from app.utils.roles import allow_add_news, allow_update, allow_create_admins

from app.utils.countries import Countries

user_router = APIRouter()


@user_router.get('/all', response_model=list[UserDisplay],
                 dependencies=[Depends(allow_add_news)])
async def read_users(db_session: AsyncSession = Depends(get_session)):
    users = await User.get_all(db_session)
    return users


@user_router.get('/me', response_model=UserDisplayFull)
async def get_me(current_user: UserDisplay = Depends(get_current_user)):
    return current_user


@user_router.get('/{user_id}', response_model=UserDisplayFull,
                 dependencies=[Depends(allow_update)])
async def get_user(user_id: int, db_session: AsyncSession = Depends(get_session),
                   current_user: UserDisplay = Depends(get_current_user)):
    user = await User.get_by_id(db_session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    return user


@user_router.post('/create', response_model=UserDisplayFull, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db_session: AsyncSession = Depends(get_session)):
    exist_user = await User.verify_email_exist(db_session, user.email)
    if exist_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system"
        )
    new_user = await User.user_registration(db_session, user)
    return new_user


@user_router.put('/update', response_model=UserDisplayFull, status_code=status.HTTP_202_ACCEPTED,
                 dependencies=[Depends(allow_update)])
async def update_user(user: UserUpdate, db_session: AsyncSession = Depends(get_session),
                      current_user: UserDisplay = Depends(get_current_user)):
    await User.user_update(db_session, user)
    updated = await User.get_by_id(db_session, user.id)
    return updated


@user_router.put('/me/update', response_model=UserDisplayFull, status_code=status.HTTP_202_ACCEPTED)
async def update_me(user: UserUpdateMe, db_session: AsyncSession = Depends(get_session),
                    current_user: UserDisplay = Depends(get_current_user)):
    exist_user = await User.get_by_id(db_session, current_user.id)
    if not exist_user:
        raise HTTPException(
            status_code=400,
            detail="User Not Found"
        )
    await User.user_update(db_session, UserUpdate(id=exist_user.id, **user.dict()))
    updated = await User.get_by_id(db_session, current_user.id)
    return updated


@user_router.put('/set_admin', response_model=UserDisplayFull, status_code=status.HTTP_202_ACCEPTED,
                 dependencies=[Depends(allow_create_admins)])
async def set_admin(email: str, db_session: AsyncSession = Depends(get_session),
                    current_user: UserDisplay = Depends(get_current_user)):
    exist_user = await User.verify_email_exist(db_session, email)
    if not exist_user:
        raise HTTPException(
            status_code=400,
            detail="User Not Found"
        )
    await User.update_admin_role(db_session, exist_user)
    updated = await User.get_by_id(db_session, current_user.id)
    return updated


@user_router.delete('/{user_id}', response_model=dict,
                    dependencies=[Depends(allow_update)])
async def delete_user(user_id: int, db_session: AsyncSession = Depends(get_session),
                      current_user: UserDisplay = Depends(get_current_user)):
    user = await User.get_by_id(db_session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    success = await User.delete_by_id(db_session, user_id)

    return {'user': user_id, 'success': success}
