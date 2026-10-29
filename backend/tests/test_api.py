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