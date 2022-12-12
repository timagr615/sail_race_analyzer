import os
from datetime import datetime

from app.core.config import settings


def generate_time() -> str:
    date = datetime.utcnow()
    return date.strftime("%Y%m")


def generate_path(username: str) -> str:
    storage_path = settings.file_storage_path + '/' + username + '/' + generate_time() + '/'
    full_path = os.path.join(os.getcwd(), storage_path)
    return full_path


def generate_filename(filename: str) -> str:
    date = datetime.utcnow()
    name = filename.lower().split('.csv')
    name = name[0] + '_' + date.strftime("%d%H%M%S") + '.csv'
    return name
