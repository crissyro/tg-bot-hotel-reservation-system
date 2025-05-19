from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from models.postgres_models import Booking, BookingStatusEnum
from datetime import datetime

class BookingCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_booking(self, total_price, user_id, room_id, check_in, check_out, status=BookingStatusEnum.ACTIVE, paid=False):
        booking = Booking(
            total_price=total_price,
            user_id=user_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            status=status, 
            paid=paid
        )
        self.session.add(booking)
        await self.session.flush()
        return booking

    async def get_user_bookings(self, user_id: int):
        result = await self.session.execute(
            select(Booking).where(Booking.user_id == user_id)
        )
        return result.scalars().all()

    async def get_all_bookings(self):
        result = await self.session.execute(select(Booking))
        return result.scalars().all()

    async def get_active_bookings(self):
        now = datetime.now()
        result = await self.session.execute(
            select(Booking).where(Booking.check_out > now)
        )
        return result.scalars().all()
    
    async def get_active_bookings_by_user_id(self, user_id: int):
        stmt = select(Booking).where(
            Booking.user_id == user_id,
            Booking.status == BookingStatusEnum.ACTIVE
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def cancel_booking(self, booking_id: int):
        stmt = update(Booking).where(Booking.id == booking_id).values(status=BookingStatusEnum.CANCELLED)
        await self.session.execute(stmt)
        await self.session.commit()

    async def mark_as_paid(self, booking_id: int):
        stmt = update(Booking).where(Booking.id == booking_id).values(paid=True)
        await self.session.execute(stmt)
        await self.session.commit()
        
    async def get_active_bookings_by_user_id(self, user_id: int):
        now = datetime.now()
        stmt = select(Booking).where(
            Booking.user_id == user_id,
            Booking.status == BookingStatusEnum.ACTIVE,
            Booking.check_out > now
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_unpaid_bookings_by_user_id(self, user_id: int):
        now = datetime.now()
        stmt = select(Booking).where(
            Booking.user_id == user_id,
            Booking.status == BookingStatusEnum.ACTIVE,
            Booking.check_out > now,
            Booking.paid == False
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()