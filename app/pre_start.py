import asyncio
import os
import time
from app.users.models import User
from app.core.db import async_session
from app.core.config import settings


async def pre_start():
    time.sleep(7)
    async with async_session() as session:
        await User.create_superuser(session)


if __name__ == '__main__':
    asyncio.run(pre_start())