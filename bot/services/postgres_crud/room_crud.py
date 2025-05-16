from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from models.postgres_models import Room, Booking

class RoomCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_room(self, number: str, room_type: str, price: float, description: str):
        new_room = Room(
            number=number,
            type=room_type,
            price=price,
            description=description
        )
        self.session.add(new_room)
        await self.session.commit()
        return new_room

    async def get_available_rooms(self, start_date: datetime, end_date: datetime):
        subquery = select(Booking.room_id).where(
            and_(
                Booking.check_in <= end_date,
                Booking.check_out >= start_date
            )
        )
        result = await self.session.execute(
            select(Room).where(
                Room.is_available == True,
                Room.id.not_in(subquery)
            )
        )
        return result.scalars().all()

    async def update_room_price(self, room_id: int, new_price: float):
        stmt = update(Room).where(Room.id == room_id).values(price=new_price)
        await self.session.execute(stmt)
        await self.session.commit()