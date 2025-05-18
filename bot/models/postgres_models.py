from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
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

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True)
    number = Column(String(10), unique=True)
    type = Column(String(50))
    price = Column(Numeric(10, 2))
    is_available = Column(Boolean, default=True)
    description = Column(String(500))

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    status = Column(String(20), default="pending")

    user = relationship("User", back_populates="bookings")
    room = relationship("Room")

class RestaurantOrder(Base):
    __tablename__ = "restaurant_orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    items = Column(String(1000))
    total = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class BarOrder(Base):
    __tablename__ = "bar_orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    items = Column(String(1000))
    total = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)