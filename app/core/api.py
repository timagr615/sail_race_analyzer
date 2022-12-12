from fastapi import APIRouter
from app.users.router import user_router
from app.auth.router import auth_router
from app.news.router import news_router
from app.saildata.router import sail_router

api_router = APIRouter()
api_router.include_router(user_router, prefix='/user', tags=['users'])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(news_router, prefix='/news', tags=['news'])
api_router.include_router(sail_router, prefix='/datafile', tags=['data'])
