from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, not_, select, update
from models.postgres_models import Booking, Room

class RoomCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_room(self, number: str, room_type: str, price: float, description: str = ""):
        new_room = Room(
            number=number,
            type=room_type,
            price=price,
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
    
async def create_initial_rooms(session: AsyncSession):
    room_crud = RoomCRUD(session)
    
    for i in range(1, 21):
        await room_crud.create_room(f"E{i:03}", "economy", 2000, "Бюджетный номер")
    
    for i in range(1, 71):
        await room_crud.create_room(f"S{i:03}", "standard", 3500, "Стандартный номер")
    
    for i in range(1, 21):
        await room_crud.create_room(f"B{i:03}", "business", 6000, "Бизнес-класс")
    
    for i in range(1, 11):
        await room_crud.create_room(f"V{i:03}", "vip", 12000, "VIP-апартаменты")