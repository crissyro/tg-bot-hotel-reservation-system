from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.db.models import User

async def get_user_by_tg_id(session: AsyncSession, tg_id: int):
    stmt = select(User).where(User.telegram_id == tg_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, tg_id: int, username: str):
    user = User(telegram_id=tg_id, username=username)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user