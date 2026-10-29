import json
import os
from contextlib import asynccontextmanager

import redis
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine, get_db
from .models import Car, Lead
from .seed import seed

CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))
_redis = None


def get_cache():
    """Redis-клиент или None, если REDIS_URL не задан (например, в тестах)."""
    global _redis
    url = os.getenv("REDIS_URL")
    if not url:
        return None
    if _redis is None:
        _redis = redis.Redis.from_url(url, decode_responses=True, socket_timeout=1)
    return _redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(title="Maison Auto API", lifespan=lifespan)


def car_dict(c: Car) -> dict:
    return {k: getattr(c, k) for k in ("id", "brand", "name", "img", "type", "price", "hp", "acc", "engine", "drive")}


class LeadIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=200)
    car_id: int | None = None
    message: str = Field(default="", max_length=1000)


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/api/cars")
def list_cars(brand: str | None = None, db: Session = Depends(get_db)):
    key = f"cars:{brand or 'all'}"
    cache = get_cache()
    if cache:
        try:
            hit = cache.get(key)
            if hit:
                return json.loads(hit)
        except redis.RedisError:
            pass

    stmt = select(Car).order_by(Car.id)
    if brand:
        stmt = stmt.where(Car.brand == brand)
    data = [car_dict(c) for c in db.scalars(stmt)]

    if cache:
        try:
            cache.setex(key, CACHE_TTL, json.dumps(data))
        except redis.RedisError:
            pass
    return data


@app.get("/api/cars/{car_id}")
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.get(Car, car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    return car_dict(car)


@app.post("/api/leads", status_code=201)
def create_lead(body: LeadIn, db: Session = Depends(get_db)):
    if body.car_id is not None and db.get(Car, body.car_id) is None:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    lead = Lead(**body.model_dump())
    db.add(lead)
    db.commit()
    return {"id": lead.id}
