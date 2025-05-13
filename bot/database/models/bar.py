from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class BarItem(Base):
    __tablename__ = "bar_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    price: Mapped[float]
