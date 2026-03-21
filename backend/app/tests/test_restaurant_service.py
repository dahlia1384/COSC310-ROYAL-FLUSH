import pytest
from fastapi import HTTPException
from app.services import restaurants_service
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate


def test_list_restaurants_returns_all_restaurants(monkeypatch: pytest.MonkeyPatch):
    fake_restaurants = [
        {
            "id": "r1",
            "name": "Spice House",
            "cuisine": "Indian",
            "address": "123 Main St",
        },
        {
            "id": "r2",
            "name": "Roma Nord Bistro",
            "cuisine": "Italian",
            "address": "456 Oak Ave",
        },
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)

    restaurants = restaurants_service.list_restaurants()

    assert len(restaurants) == 2  # checks that both restaurants are returned
    assert restaurants[0].name == "Spice House"  # checks first restaurant name is correct
    assert restaurants[1].name == "Roma Nord Bistro"  # checks second restaurant name is correct


def test_create_restaurant_adds_new_restaurant(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(restaurants_service, "load_all", lambda: [])

    saved = {}
    monkeypatch.setattr(
        restaurants_service,
        "save_all",
        lambda restaurants: saved.setdefault("restaurants", restaurants)
    )

    payload = RestaurantCreate(
        name="  Spice House  ",
        cuisine=" Indian ",
        address=" 123 Main St "
    )

    restaurant = restaurants_service.create_restaurant(payload)

    assert restaurant.name == "Spice House"  # checks that whitespace is removed from the name
    assert restaurant.cuisine == "Indian"  # checks that whitespace is removed from the cuisine
    assert restaurant.address == "123 Main St"  # checks that whitespace is removed from the address
    assert len(saved["restaurants"]) == 1  # checks that one restaurant was saved
    assert saved["restaurants"][0]["name"] == "Spice House"  # checks that the saved restaurant name is correct


def test_create_restaurant_with_blank_name_raises_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(restaurants_service, "load_all", lambda: [])
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    payload = RestaurantCreate(
        name="   ",
        cuisine="Indian",
        address="123 Main St"
    )

    with pytest.raises(HTTPException) as exc:
        restaurants_service.create_restaurant(payload)

    assert exc.value.status_code == 400  # checks that blank names are rejected
    assert exc.value.detail == "Restaurant name cannot be empty."  # checks that the output is the expected error message


def test_get_restaurant_by_id_returns_matching_restaurant(monkeypatch: pytest.MonkeyPatch):
    fake_restaurants = [
        {
            "id": "r1",
            "name": "Spice House",
            "cuisine": "Indian",
            "address": "123 Main St",
        }
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)

    restaurant = restaurants_service.get_restaurant_by_id("r1")

    assert restaurant.id == "r1"  # checks that the correct restaurant was returned
    assert restaurant.name == "Spice House"  # checks that the restaurant name is correct


def test_get_restaurant_by_id_raises_404_when_missing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(restaurants_service, "load_all", lambda: [])

    with pytest.raises(HTTPException) as exc:
        restaurants_service.get_restaurant_by_id("missing")

    assert exc.value.status_code == 404  # checks that missing restaurant returns 404
    assert "not found" in exc.value.detail.lower()  # checks that the output is the expected error message


def test_update_restaurant_updates_existing_restaurant(monkeypatch: pytest.MonkeyPatch):
    fake_restaurants = [
        {
            "id": "r1",
            "name": "Spice House",
            "cuisine": "Indian",
            "address": "123 Main St",
        }
    ]

    saved = {}

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(
        restaurants_service,
        "save_all",
        lambda restaurants: saved.setdefault("restaurants", restaurants)
    )

    payload = RestaurantUpdate(
        name="  Spice Garden  ",
        cuisine=" Indian Fusion ",
        address=" 789 Elm St "
    )

    updated_restaurant = restaurants_service.update_restaurant("r1", payload)

    assert updated_restaurant.name == "Spice Garden"  # checks that the updated name is correct
    assert updated_restaurant.cuisine == "Indian Fusion"  # checks that the updated cuisine is correct
    assert updated_restaurant.address == "789 Elm St"  # checks that the updated address is correct
    assert saved["restaurants"][0]["name"] == "Spice Garden"  # checks that the saved data was updated correctly


def test_update_restaurant_with_blank_name_raises_error(monkeypatch: pytest.MonkeyPatch):
    fake_restaurants = [
        {
            "id": "r1",
            "name": "Spice House",
            "cuisine": "Indian",
            "address": "123 Main St",
        }
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    payload = RestaurantUpdate(
        name="   ",
        cuisine="Indian",
        address="123 Main St"
    )

    with pytest.raises(HTTPException) as exc:
        restaurants_service.update_restaurant("r1", payload)

    assert exc.value.status_code == 400  # checks that blank updated names are rejected too
    assert exc.value.detail == "Restaurant name cannot be empty."  # checks that the output is the expected error message


def test_update_restaurant_raises_404_when_missing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(restaurants_service, "load_all", lambda: [])
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    payload = RestaurantUpdate(
        name="Spice Garden",
        cuisine="Indian Fusion",
        address="789 Elm St"
    )

    with pytest.raises(HTTPException) as exc:
        restaurants_service.update_restaurant("missing", payload)

    assert exc.value.status_code == 404  # checks that updating a missing restaurant returns 404
    assert "not found" in exc.value.detail.lower()  # checks that the output is the expected error message


def test_delete_restaurant_removes_existing_restaurant(monkeypatch: pytest.MonkeyPatch):
    fake_restaurants = [
        {
            "id": "r1",
            "name": "Spice House",
            "cuisine": "Indian",
            "address": "123 Main St",
        },
        {
            "id": "r2",
            "name": "Roma Nord Bistro",
            "cuisine": "Italian",
            "address": "456 Oak Ave",
        },
    ]

    saved = {}

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(
        restaurants_service,
        "save_all",
        lambda restaurants: saved.setdefault("restaurants", restaurants)
    )

    restaurants_service.delete_restaurant("r1")

    assert len(saved["restaurants"]) == 1  # checks to make sure that only one restaurant was deleted
    assert saved["restaurants"][0]["id"] == "r2"  # checks that the correct restaurant remains


def test_delete_restaurant_raises_404_when_missing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(restaurants_service, "load_all", lambda: [])
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    with pytest.raises(HTTPException) as exc:
        restaurants_service.delete_restaurant("missing")

    assert exc.value.status_code == 404  # checks that deleting a missing restaurant returns 404
    assert "not found" in exc.value.detail.lower()  # checks that the output is the expected error message

def test_delete_restaurant_with_completed_orders_succeeds(monkeypatch):
    fake_restaurants = [
        {
            "id": "r1",
            "name": "Spice House",
            "cuisine": "Indian",
            "address": "123 Main St",
        }
    ]

    saved = {}

    monkeypatch.setattr(restaurant_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurant_service, "has_unfinished_orders", lambda restaurant_id: False)
    monkeypatch.setattr(
        restaurant_service,
        "save_all",
        lambda restaurants: saved.setdefault("restaurants", restaurants)
    )

    restaurant_service.delete_restaurant("r1")

    assert saved["restaurants"] == []  # checks that the restaurant was deleted when no unfinished orders exist


def test_delete_restaurant_with_pending_orders_raises_error(monkeypatch):
    fake_restaurants = [
        {
            "id": "r1",
            "name": "Spice House",
            "cuisine": "Indian",
            "address": "123 Main St",
        }
    ]

    monkeypatch.setattr(restaurant_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurant_service, "has_unfinished_orders", lambda restaurant_id: True)
    monkeypatch.setattr(restaurant_service, "save_all", lambda restaurants: None)

    with pytest.raises(HTTPException) as exc:
        restaurant_service.delete_restaurant("r1")

    assert exc.value.status_code == 400  # checks that deletion is blocked for unfinished orders
    assert "pending or active orders" in exc.value.detail.lower()  # checks the error message


def test_delete_restaurant_with_active_orders_raises_error(monkeypatch):
    fake_restaurants = [
        {
            "id": "r1",
            "name": "Spice House",
            "cuisine": "Indian",
            "address": "123 Main St",
        }
    ]

    monkeypatch.setattr(restaurant_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurant_service, "has_unfinished_orders", lambda restaurant_id: True)
    monkeypatch.setattr(restaurant_service, "save_all", lambda restaurants: None)

    with pytest.raises(HTTPException) as exc:
        restaurant_service.delete_restaurant("r1")

    assert exc.value.status_code == 400  # checks that deletion is blocked for active orders too
    assert "pending or active orders" in exc.value.detail.lower()  # checks the error message