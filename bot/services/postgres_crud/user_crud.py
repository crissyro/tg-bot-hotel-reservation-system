from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models.postgres_models import User, Booking, RestaurantOrder, BarOrder

class UserCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, telegram_id: int, name: str, surname: str):
        new_user = User(telegram_id=telegram_id, name=name, surname=surname)
        self.session.add(new_user)
        await self.session.commit()
        return new_user

    async def get_user(self, user_id: int):
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_telegram_id(self, telegram_id: int):
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, **kwargs):
        stmt = update(User).where(User.id == user_id).values(**kwargs)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_user(self, user_id: int):
        await self.session.execute(delete(Booking).where(Booking.user_id == user_id))
        await self.session.execute(delete(RestaurantOrder).where(RestaurantOrder.user_id == user_id))
        await self.session.execute(delete(BarOrder).where(BarOrder.user_id == user_id))
        await self.session.execute(delete(User).where(User.id == user_id))
        await self.session.commit()