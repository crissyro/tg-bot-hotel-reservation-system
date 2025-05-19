from datetime import datetime, timedelta
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, case, func, not_, select
from models.postgres_models import Booking, BookingStatusEnum, Room, RoomStatusEnum

class RoomCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_room(self, number: str, human_name: str, room_type: str, 
                        price: float, capacity: int, description: str = ""):
            new_room = Room(
                number=number,
                human_name=human_name,
                type=room_type,
                price=price,
                capacity=capacity,
                description=description
            )
            self.session.add(new_room)
            await self.session.flush()
            return new_room

    async def update_room_status(self, room_id: int, status: RoomStatusEnum):
        room = await self.get_room_by_id(room_id)
        if room:
            room.status = status

    async def get_room(self, room_id: int):
        result = await self.session.execute(
            select(Room).where(Room.id == room_id)
            )
        return result.scalar_one_or_none()

    async def get_all_rooms_paginated(self, page: int = 1, per_page: int = 10):
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
                    Room.status == RoomStatusEnum.AVAILABLE,
                    not_(Room.id.in_(subquery))
            ))
            return result.scalars().all()
        except Exception as e:
            logging.error(f"Error getting available rooms: {str(e)}")
            return []

    async def get_room_by_id(self, room_id: int):
        result = await self.session.execute(
            select(Room).where(Room.id == room_id)
        )
        return result.scalars().first()

    async def get_all_rooms(self):
        result = await self.session.execute(select(Room))
        return result.scalars().all()
    
    async def get_rooms_statistics(self):
        income = await self.session.execute(
            select(func.sum(Booking.total_price))
            )
        total_income = income.scalar() or 0

        rooms_status = await self.session.execute(
            select(
                func.count(Room.id),
                func.sum(case((Room.status == RoomStatusEnum.AVAILABLE, 1), else_=0))
            )
        )
        total_rooms, available_rooms = rooms_status.first()

        bookings_count = await self.session.execute(
            select(func.count(Booking.id))
        )
            
        return {
            "total_income": total_income,
            "total_rooms": total_rooms,
            "available_rooms": available_rooms,
            "total_bookings": bookings_count.scalar()
        }

    async def refresh_rooms_availability(self):
        rooms = await self.get_all_rooms()
        for room in rooms:
            active_bookings = await self.session.execute(
                select(Booking).where(
                    and_(
                        Booking.room_id == room.id,
                        Booking.check_out >= datetime.now(),
                        Booking.status == BookingStatusEnum.ACTIVE
                    )
                )
            )
            if active_bookings.scalars().first():
                room.status = RoomStatusEnum.BOOKED
            else:
                if room.status != RoomStatusEnum.MAINTENANCE and room.status != RoomStatusEnum.CLOSED:
                    room.status = RoomStatusEnum.AVAILABLE
        await self.session.commit()

    async def auto_update_statuses(self):
        rooms = await self.get_all_rooms()
        for room in rooms:
            if room.status == RoomStatusEnum.BOOKED:
                bookings = await self.session.execute(
                    select(Booking).where(
                        Booking.room_id == room.id,
                        Booking.check_out < datetime.now()
                    )
                )
                if not bookings.scalars().all():
                    room.status = RoomStatusEnum.AVAILABLE

    async def get_rooms_by_ids(self, ids: list[int]) -> list:
        result = await self.session.execute(
            select(Room).where(Room.id.in_(ids))
        )
        return result.scalars().all()

async def create_initial_rooms(session: AsyncSession):
    room_crud = RoomCRUD(session)
    types_config = [
            ("economy", "Эконом", 8, 2000, 2),
            ("standard", "Стандарт", 12, 3500, 3),
            ("business", "Бизнес", 3, 6000, 4),
            ("vip", "VIP", 2, 12000, 6)
    ]
    
    for room_type, human_name, count, price, capacity in types_config:
        for i in range(1, count + 1):
            await room_crud.create_room(
                number=f"{room_type[0].upper()}{i:03}",
                human_name=human_name,
                room_type=room_type,
                price=price,
                capacity=capacity,
                description=f"{room_type.capitalize()} номер"
            )