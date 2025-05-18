from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, not_, select, update
from models.postgres_models import Booking, Room

class RoomCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_room(self, number: str, room_type: str, price: float, capacity: int, description: str = ""):
        new_room = Room(
            number=number,
            type=room_type,
            price=price,
            capacity=capacity,
            description=description
        )
        self.session.add(new_room)
        await self.session.commit()
        return new_room

    async def update_room_status(self, room_id: int, is_available: bool):
        stmt = update(Room).where(Room.id == room_id).values(is_available=is_available)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_room(self, room_id: int):
        result = await self.session.execute(select(Room).where(Room.id == room_id))
        return result.scalar_one_or_none()

    async def get_all_rooms(self, page: int = 1, per_page: int = 10):
        offset = (page - 1) * per_page
        result = await self.session.execute(
            select(Room)
            .offset(offset)
            .limit(per_page)
        )
        return result.scalars().all()

    async def get_rooms_by_type(self, room_type: str):
        result = await self.session.execute(
            select(Room).where(Room.type == room_type)
        )
        return result.scalars().all()
    
    async def get_available_rooms(self, check_in: datetime, check_out: datetime):
        try:
            subquery = select(Booking.room_id).where(
                and_(
                    Booking.check_in <= check_out,
                    Booking.check_out >= check_in
                )
            )
            
            result = await self.session.execute(
                select(Room).where(
                    Room.is_available == True,
                    not_(Room.id.in_(subquery))
                )
            )
            return result.scalars().all()
        except Exception as e:
            logging.error(f"Error getting available rooms: {str(e)}")
            return []
        
    async def get_room_by_id(self, room_id: int):
        result = await self.session.execute(
            select(Room).where(Room.id == room_id)
        )
        return result.scalar_one_or_none()

    async def get_all_rooms(self):
        result = await self.session.execute(select(Room))
        return result.scalars().all()
    
async def create_initial_rooms(session: AsyncSession):
    room_crud = RoomCRUD(session)
    
    types_config = [
        ("economy", 20, 2000, 2),
        ("standard", 70, 3500, 3),
        ("business", 20, 6000, 4),
        ("vip", 10, 12000, 6)
    ]
    
    for room_type, count, price, capacity in types_config:
        for i in range(1, count + 1):
            await room_crud.create_room(
                number=f"{room_type[0].upper()}{i:03}",
                room_type=room_type,
                price=price,
                capacity=capacity,
                description=f"{room_type.capitalize()} номер"
            )