from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    check_in: Mapped[Date]
    check_out: Mapped[Date]
    is_paid: Mapped[bool] = mapped_column(default=False)
