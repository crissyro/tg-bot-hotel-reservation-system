from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.postgres_models import Booking
from datetime import datetime

class BookingCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_booking(self, user_id: int, room_id: int, 
                           check_in: datetime, check_out: datetime):
        new_booking = Booking(
            user_id=user_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out
        )
        self.session.add(new_booking)
        await self.session.commit()
        return new_booking

    async def get_user_bookings(self, user_id: int):
        result = await self.session.execute(
            select(Booking).where(Booking.user_id == user_id)
        )
        return result.scalars().all()

    async def cancel_booking(self, booking_id: int):
        await self.session.execute(delete(Booking).where(Booking.id == booking_id))
        await self.session.commit()