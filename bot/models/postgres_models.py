from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from services.postgres_database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    name = Column(String(64))
    surname = Column(String(64))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")


class RoomStatusEnum(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"
    
    @property
    def emoji(self):
        return {
            self.AVAILABLE: "✅",
            self.BOOKED: "⛔",
            self.MAINTENANCE: "🛠",
            self.CLOSED: "🔒"
        }.get(self, "")

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True)
    number = Column(String(10), unique=True)
    human_name = Column(String(50))
    type = Column(String(20), nullable=False) 
    price = Column(Numeric(10, 2), nullable=False)
    capacity = Column(Integer)
    description = Column(String(500))
    status = Column(
        SQLAlchemyEnum(RoomStatusEnum, values_callable=lambda x: [e.value for e in x]), 
        default=RoomStatusEnum.AVAILABLE
    )
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True)
    total_price = Column(Numeric(10, 2))
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    status = Column(
        SQLAlchemyEnum(
            RoomStatusEnum, 
            values_callable=lambda x: [e.value for e in x]  
        ), 
        default=RoomStatusEnum.AVAILABLE
    )
    user = relationship("User", back_populates="bookings")
    room = relationship("Room")

class RestaurantOrder(Base):
    __tablename__ = "restaurant_orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    items = Column(String(1000))
    total = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), default=datetime.now)

class BarOrder(Base):
    __tablename__ = "bar_orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    items = Column(String(1000))
    total = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), default=datetime.now)