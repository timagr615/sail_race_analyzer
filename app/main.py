from fastapi import FastAPI

from app.api.api import api_router
from .config import settings
from app.models.db import init_models


app = FastAPI()
app.include_router(api_router)


@app.on_event("startup")
async def on_startup():
    await init_models()


@app.get('/')
async def root():
    return {'app name': settings.app_name,
            'admin': settings.admin_email,
            'db': settings.database_url}
