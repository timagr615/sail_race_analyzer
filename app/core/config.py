import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'Sail Race Analyzer'
    admin_email: str
    admin_firstname: str
    admin_password: str
    admin_username: str
    admin_lastname: str

    database_url: str
    secret_key: str
    access_token_expire_minutes: int
    file_storage_path: str

    celery_broker_url2: str
    celery_result_backend: str

    class Config:
        env_file = ".env"


settings = Settings()