import asyncio
import os.path

from sqlalchemy.ext.asyncio import AsyncSession
from app.saildata.models import SailData


async def change_file_size(session: AsyncSession, path: str) -> None:
    await asyncio.sleep(10)
    size = os.path.getsize(path)
    await SailData.update_file_size(session, size, path)