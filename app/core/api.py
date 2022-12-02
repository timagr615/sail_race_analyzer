from fastapi import APIRouter
from app.users.router import user_router
from app.auth.router import auth_router

api_router = APIRouter()
api_router.include_router(user_router, prefix='/user', tags=['users'])
api_router.include_router(auth_router, tags=["auth"])