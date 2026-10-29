from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Car

CARS = [
    ("Mercedes-Benz", "S 580 4MATIC", "mercedes-s580", "sedan", 126000, 496, 4.4, "4.0 V8 biturbo, mild hybrid", "Полный"),
    ("Mercedes-Benz", "AMG G 63", "mercedes-g63", "suv", 180000, 577, 4.4, "4.0 V8 biturbo", "Полный"),
    ("BMW", "M5", "bmw-m5", "sedan", 120000, 717, 3.4, "4.4 V8 + электро (гибрид)", "Полный"),
    ("BMW", "X7 xDrive40i", "bmw-x7", "suv", 87000, 375, 5.8, "3.0 R6 turbo, mild hybrid", "Полный"),
    ("Audi", "RS 7 Sportback", "audi-rs7", "sedan", 130000, 621, 3.5, "4.0 V8 biturbo, mild hybrid", "Полный"),
    ("Audi", "RS Q8", "audi-rsq8", "suv", 116000, 591, 3.6, "4.0 V8 biturbo, mild hybrid", "Полный"),
    ("Porsche", "911 Carrera S", "porsche-911", "coupe", 143000, 443, 3.0, "3.0 H6 biturbo", "Задний"),
    ("Lexus", "LC 500", "lexus-lc500", "coupe", 101000, 471, 4.4, "5.0 V8", "Задний"),
]


def seed(db: Session) -> None:
    if db.scalar(select(Car.id).limit(1)) is not None:
        return
    db.add_all(
        Car(brand=b, name=n, img=i, type=t, price=p, hp=h, acc=a, engine=e, drive=d)
        for b, n, i, t, p, h, a, e, d in CARS
    )
    db.commit()
