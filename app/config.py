import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'Sail Race Analyzer'
    admin_email: str
    database_url: str

    class Config:
        env_file = ".env"
'''RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
        libressl-dev libffi-dev gcc musl-dev python3-dev \
        postgresql-dev \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r /usr/src/requirements.txt \
    && rm -rf /root/.cache/pip'''
#32700
'''backend:
    build: .
    command: uvicorn app.main:app --reload --host 0.0.0.0
    env_file:
      - ".env"
    volumes:
      - .:/usr/src/
    ports:
      - 8002:8000
    environment:
      - DATABASE_URL=${DATABASE_URL}'''
settings = Settings()