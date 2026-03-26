from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_restaurants_returns_200():
    response = client.get("/restaurants")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_filter_restaurants_by_cuisine():
    response = client.get("/restaurants?cuisine=Indian")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for restaurant in data:
        assert restaurant["cuisine"] == "Indian"


def test_filter_restaurants_by_min_rating():
    response = client.get("/restaurants?min_rating=4.0")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for restaurant in data:
        assert restaurant["rating"] >= 4.0


def test_filter_restaurants_by_cuisine_and_rating():
    response = client.get("/restaurants?cuisine=Italian&min_rating=3.0")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for restaurant in data:
        assert restaurant["cuisine"] == "Italian"
        assert restaurant["rating"] >= 3.0