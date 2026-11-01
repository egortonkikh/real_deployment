def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_cars(client):
    cars = client.get("/api/cars").json()
    assert len(cars) == 8
    assert all(c["price"] > 0 and c["hp"] > 0 for c in cars)


def test_filter_by_brand(client):
    cars = client.get("/api/cars", params={"brand": "BMW"}).json()
    assert len(cars) == 2
    assert {c["brand"] for c in cars} == {"BMW"}


def test_get_car_and_404(client):
    first = client.get("/api/cars").json()[0]
    assert client.get(f"/api/cars/{first['id']}").json()["name"] == first["name"]
    assert client.get("/api/cars/9999").status_code == 404


def test_create_lead(client):
    r = client.post("/api/leads", json={"name": "Егор", "email": "test@example.com", "car_id": 1})
    assert r.status_code == 201
    assert "id" in r.json()


def test_lead_validation(client):
    assert client.post("/api/leads", json={"name": "Егор", "email": "not-an-email"}).status_code == 422
    assert client.post("/api/leads", json={"name": "Егор", "email": "a@b.co", "car_id": 9999}).status_code == 404
def test_list_cars_uses_cache(client, fake_cache):
    """Первый вызов пишет в кэш, второй — читает из него."""
    # Первый вызов: должен записать в кэш (строки 76-79)
    r1 = client.get("/api/cars")
    assert r1.status_code == 200
    assert len(r1.json()) == 8

    # Проверяем, что кэш реально записан
    cached = fake_cache.get("cars:all")
    assert cached is not None, "Кэш не был записан после первого вызова"

    # Второй вызов: должен читать из кэша (строки 63-68)
    r2 = client.get("/api/cars")
    assert r2.status_code == 200
    assert r2.json() == r1.json()


def test_list_cars_survives_redis_error(client, fake_cache):
    """Если Redis падает — запрос проходит через БД (except RedisError)."""
    import redis as redis_module

    def raise_error(*args, **kwargs):
        raise redis_module.RedisError("simulated failure")

    # Подменяем методы fake-клиента, чтобы они бросали RedisError
    fake_cache.get = raise_error
    fake_cache.setex = raise_error

    # Запрос должен пройти — except RedisError сработает, fallback на БД
    r = client.get("/api/cars")
    assert r.status_code == 200
    assert len(r.json()) == 8

def test_create_car_invalidates_cache(client, fake_cache):
    """После создания новой машины кэш списка должен инвалидироваться."""
    # Прогреваем кэш списком из 8 машин
    r1 = client.get("/api/cars")
    assert len(r1.json()) == 8

    # Создаём новую машину
    new_car = {
        "brand": "Rolls-Royce",
        "name": "Phantom",
        "img": "rolls-phantom",
        "type": "sedan",
        "price": 500000,
        "hp": 563,
        "acc": 4.6,
        "engine": "6.75 V12",
        "drive": "Задний",
    }
    r = client.post("/api/cars", json=new_car)
    assert r.status_code == 201
    assert "id" in r.json()

    # Список должен содержать уже 9 машин — НО если кэш не инвалидирован,
    # мы получим 8 (старый закэшированный список)
    r2 = client.get("/api/cars")
    assert len(r2.json()) == 9, "Кэш не инвалидирован — новая машина не видна в списке"