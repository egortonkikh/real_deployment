from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(100))
    img: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20))
    price: Mapped[int]
    hp: Mapped[int]
    acc: Mapped[float]
    engine: Mapped[str] = mapped_column(String(100))
    drive: Mapped[str] = mapped_column(String(30))


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200))
    car_id: Mapped[int | None]
    message: Mapped[str] = mapped_column(String(1000), default="")
