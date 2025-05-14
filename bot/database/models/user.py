from sqlalchemy import Column, Integer, BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    surname: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(64))
    patronymic: Mapped[str] = mapped_column(String(64))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    bookings = relationship("Booking", back_populates="user")
