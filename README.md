# Бекенд приложения Sail Race Analyzer
### Файлы проекта:

`/app` - каталог кода приложения 

`.env` - файл переменных окружения с данными о БД и приложении

`alembic.ini` - конфигурация alembic для миграций

`/migrations` - каталог для настройки alembic и хранения миграций

`pre_start.sh` - запускает действия перед стартом приложения

`migrate.sh` - запускает автоматические миграции

`drop_db.sh` - дропает базу данных

`Dockerfile` - файл для подъёма контейнера докер с приложением `FastAPI`

`docker-compose.yml` - файл для docker-compose, поднимающий контейнер с БД и приложением FastAPI

## Разъяснения
`Dockerfile`
```Dockerfile
FROM python:3.10.8-slim-buster
WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /usr/src/requirements.txt

RUN pip install -r /usr/src/requirements.txt

COPY . /usr/src

COPY ./pre_start.sh /usr/src
COPY ./migrate.sh /usr/src

ENV PYTHONPATH /usr/src/

RUN chmod +x /usr/src/pre_start.sh
RUN chmod +x /usr/src/migrate.sh
```
- `FROM python:3.10.8-slim-buster` -  использовать образ `python:3.10.8-slim-buster`
- `WORKDIR /usr/src` - установка рабочей директории в контейнере
- `ENV PYTHONDONTWRITEBYTECODE 1`
-  `ENV PYTHONUNBUFFERED 1` - настройка работы python
- `COPY ./requirements.txt /usr/src/requirements.txt` - копировать requirements.txt
из текущего каталога в `WORKDIR`
- `RUN pip install -r /usr/src/requirements.txt` - установить зависимости
- `COPY . /usr/src` - скопировать проект в `WORKDIR`
- `RUN chmod +x /usr/src/pre_start.sh`
- `RUN chmod +x /usr/src/migrate.sh` - устанавливает права на исполнение

`docker-compose.yml`
```yaml
version: '3.7'

services:
  backend:
    build: .
    command: sh /usr/src/pre_start.sh
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

## Шаги для настройки работы приложения
- установить зависимости из `requirements.txt`
- добавить код проекта 
- добавить файл `.env` для хранения переменных окружения: они потом используются 
в файле `config.py` и docker файлах.
- создать докер файлы: `Dockerfile и docker-compose.yml` - контейнеры для приложения,
БД postgres и pgadmin.
- Далее если в каталогах нет папки `/migrations` и файла `alembic.ini` произвести команду 
```shell
alembic init -t async migrations
```
- В появившемся файле `alembic.ini` убрать строку sqlalchemy.url
- В файле `migrations/env.py` добавить

```python
from app.core.db import Base

from app.core.config import settings
from app.users.models import User ...
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata
```

- Поднять приложение 
```shell
sudo docker compose up -d --build
```
- Если нужно обновить миграции 
```shell
sudo docker compose exec backend sh migrate.sh
```
- Если нужно дропнуть БД
```shell
sudo docker compose exec backend sh drop_bd.sh
```


### Проблемы
- Если проблема с подключением к БД, то можно дропнуть БД
- Нужно остановить контейнеры
```shell
sudo docker compose down -v
```
- Убрать локальные папки данных бд, они определены в `docker-compose.yml`
```shell
sudo rm -rf postgres_data
```
- Убрать файлы миграций из `/migrations/versions`
```shell
cd migrations
sudo rm -rf versions
mkdir versions
```
- После данных шагов надо опять поднять приложение и применить мигации

#### Команды Docker
```shell
sudo docker compose up -d --build
sudo docker compose down -v
sudo docker compose ps # Запущенные контейнеры
sudo docker compose ps -a # все контейнеры
sudo docker compose images # изображения
sudo docker compose logs -f [service name]
sudo docker compose exec [service name] [command]
# Например
sudo docker compose run -it backend bash # терминал в контейнере
sudo docker compose exec backend alembic revision --autogenerate -m "name"
sudo docker compose exec backend alembig upgrade head
sudo docker compose exec backend sh migrate.sh
sudo docker compose exec backend sh drop_bd.sh

sudo docker ps
sudo docker ps -a
sudo docker run -it [image name]
sudo docker rm [image id]
```
