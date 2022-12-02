from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


async def verify_email_exist(email: str, session: AsyncSession) -> User | None:
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    return result.scalars().first()
