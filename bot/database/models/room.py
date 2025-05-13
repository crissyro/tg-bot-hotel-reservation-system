from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str] = mapped_column(String(16)) 
    price: Mapped[float] = mapped_column()
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
