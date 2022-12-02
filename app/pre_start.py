import asyncio
import time
from app.users.models import User
from app.core.db import async_session


async def pre_start():
    time.sleep(5)
    async with async_session() as session:
        await User.create_superuser(session)


if __name__ == '__main__':
    asyncio.run(pre_start())