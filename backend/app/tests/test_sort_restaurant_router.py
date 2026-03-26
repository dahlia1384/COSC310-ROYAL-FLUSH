from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_sort_restaurants_by_rating_desc():
    response = client.get("/restaurants?sort_by=rating")

    assert response.status_code == 200

    data = response.json()
    ratings = [restaurant["rating"] for restaurant in data]

    assert ratings == sorted(ratings, reverse=True)


def test_invalid_sort_option_returns_422():
    response = client.get("/restaurants?sort_by=name")
    assert response.status_code == 422


def test_sort_restaurants_by_delivery_time_with_customer_location():
    response = client.get("/restaurants?sort_by=delivery_time&customer_location=City_2")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    if "estimated_delivery_time" in data[0]:
        delivery_times = [restaurant["estimated_delivery_time"] for restaurant in data]
        assert delivery_times == sorted(delivery_times)


def test_sort_restaurants_by_delivery_time_expected_order():
    response = client.get("/restaurants?sort_by=delivery_time&customer_location=City_2")

    assert response.status_code == 200

    data = response.json()
    returned_ids = [restaurant["id"] for restaurant in data]

    assert returned_ids[:4] == ["2", "8", "3", "4"]


def test_invalid_sort_option_returns_error():
    response = client.get("/restaurants?sort_by=bad_option")

    assert response.status_code in [400, 422]