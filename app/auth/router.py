from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.db import get_session
from app.users.models import User
from app.users import hashing
from .jwt import create_access_token


auth_router = APIRouter()


@auth_router.post('/login')
async def login(request: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await User.verify_email_exist(session, request.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    if not hashing.verify_password(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
