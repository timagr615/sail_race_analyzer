# Бекенд приложения Sail Race Analyzer
### Файлы проекта:

`/app` - каталог кода приложения 

`.env` - файл переменных окружения с данными о БД и приложении

`Dockerfile` - файл для подъёма контейнера докер с приложением `FastAPI`

`docker-compose.yml` - файл для docker-compose, поднимающий контейнер с БД и приложением FastAPI

## Разъяснения
`Dockerfile`
`````Dockerfile
    FROM python:3.10.8-slim-buster
    WORKDIR /usr/src
    
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1
    
    COPY ./requirements.txt /usr/src/requirements.txt
    
    RUN pip install -r /usr/src/requirements.txt
    
    COPY . /usr/src
`````
- `FROM python:3.10.8-slim-buster` -  использовать образ `python:3.10.8-slim-buster`
- `WORKDIR /usr/src` - установка рабочей директории в контейнере
- `ENV PYTHONDONTWRITEBYTECODE 1`
-  `ENV PYTHONUNBUFFERED 1` - настройка работы python
- `COPY ./requirements.txt /usr/src/requirements.txt` - копировать requirements.txt
из текущего каталога в `WORKDIR`
- `RUN pip install -r /usr/src/requirements.txt` - установить зависимости
- `COPY . /usr/src` - скопировать проект в `WORKDIR`

`docker-compose.yml`
```yaml
version: '3.7'

services:
  backend:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    env_file:
      - ".env"
    volumes:
      - .:/usr/src/
    ports:
      - 8002:8000
    depends_on:
      - db
  db:
    image: postgres:latest
    env_file:
      - ".env"

    volumes:
      - ./postgres_data:/var/lib/postgresql/data/pgdata
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
      POSTGRES_PORT: ${DATABASE_PORT}
      #POSTGRES_HOST: ${DATABASE_HOST}
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - 5431:5432
volumes:
  postgres_data:
```

- БЕЗ `PGDATA` приложение FastAPI не подключалось к БД
- В `DATABASE_URL` проекта FastAPI хост базы данных должен быть указан как имя сервиса `docker-compose`: db


