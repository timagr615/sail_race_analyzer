from typing import TYPE_CHECKING
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.news.schemas import NewsDB, NewsCreate, NewsUpdate
from app.users.schemas import UserDisplay
from app.core.db import get_session
#if TYPE_CHECKING:
from app.news.models import News

from app.users.models import User
from app.auth.jwt import get_current_user

from app.utils.roles import allow_add_news, allow_update, allow_create_admins

from app.utils.countries import Countries

news_router = APIRouter()


@news_router.get('/all', response_model=list[NewsDB])
async def read_news(offset: int = 0, limit: int = 100, db_session: AsyncSession = Depends(get_session)):
    news = await News.get_all(db_session, offset, limit)
    return news


@news_router.get('/{news_id}', response_model=NewsDB)
async def get_news(news_id: int,
                   db_session: AsyncSession = Depends(get_session)):
    news = await News.get_by_id(db_session, news_id)
    return news


@news_router.post('/create', response_model=NewsDB,
                  dependencies=[Depends(allow_add_news)])
async def create_news(news: NewsCreate,
                      db_session: AsyncSession = Depends(get_session),
                      current_user: UserDisplay = Depends(get_current_user)):
    news = await News.create_news(db_session, current_user.id, news)
    return news


@news_router.put('/update', response_model=NewsDB)
async def update_news(news: NewsUpdate,
                      db_session: AsyncSession = Depends(get_session),
                      current_user: UserDisplay = Depends(get_current_user)):
    current_news = await News.get_by_id(db_session, news.id)
    if current_user.id != current_news.user_id:
        raise HTTPException(
            status_code=400,
            detail="You are not publisher of this news"
        )
    news = await News.update_news(db_session, news)
    return news


@news_router.delete('/{news_id}', response_model=dict,
                    dependencies=[Depends(allow_add_news)])
async def delete_news(news_id: int, db_session: AsyncSession = Depends(get_session),
                      current_user: UserDisplay = Depends(get_current_user)):
    current_news = await News.get_by_id(db_session, news_id)
    if not current_news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News Not Found")
    success = await News.delete_by_id(db_session, news_id)

    return {'user': news_id, 'success': success}
