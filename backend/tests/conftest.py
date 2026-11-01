import os
import tempfile

# Переменные окружения нужно задать до импорта приложения.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ.pop("REDIS_URL", None)

import pytest
from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.seed import seed


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    yield

@pytest.fixture
def fake_cache(monkeypatch):
    """Подменяет redis.Redis.from_url на fakeredis.FakeRedis."""
    import fakeredis
    import redis as redis_module
    import app.main as main_module

    fake = fakeredis.FakeRedis(decode_responses=True)

    monkeypatch.setattr(
        redis_module.Redis, "from_url",
        classmethod(lambda cls, *args, **kwargs: fake),
    )
    monkeypatch.setattr(main_module, "_redis", None)
    monkeypatch.setenv("REDIS_URL", "redis://fake:6379/0")

    return fake

def pytest_sessionfinish(session, exitstatus):
    os.unlink(_tmp.name)
