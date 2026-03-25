import pytest
from fastapi import HTTPException
from app.services import restaurants_service
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate


def test_list_restaurants_returns_all_restaurants(monkeypatch: pytest.MonkeyPatch):
    fake_restaurants = [
        {"id": "r1", "name": "Spice House", "cuisine": "Indian", "address": "123 Main St"},
        {"id": "r2", "name": "Roma Nord Bistro", "cuisine": "Italian", "address": "456 Oak Ave"},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)

    restaurants = restaurants_service.list_restaurants()

    assert len(restaurants) == 2
    assert restaurants[0].name == "Spice House"
    assert restaurants[1].name == "Roma Nord Bistro"


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

    assert restaurant.name == "Spice House"
    assert restaurant.cuisine == "Indian"
    assert restaurant.address == "123 Main St"
    assert len(saved["restaurants"]) == 1


def test_delete_restaurant_when_missing_does_not_raise(monkeypatch):
    monkeypatch.setattr(restaurants_service, "load_all", lambda: [])
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    result = restaurants_service.delete_restaurant("missing")

    assert result is None


def test_delete_restaurant_with_pending_orders_does_not_raise(monkeypatch):
    fake_restaurants = [{"id": "r1", "name": "Spice House", "cuisine": "Indian", "address": "123 Main St"}]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "has_unfinished_orders", lambda restaurant_id: True)
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    result = restaurants_service.delete_restaurant("r1")

    assert result is None


def test_search_by_restaurant_name(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
        {"id": "r2", "name": "Burger Spot", "cuisine": "Fast Food", "address": "Kelowna"},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])

    results = restaurants_service.list_restaurants(keyword="Tokyo")

<<<<<<< HEAD
    assert exc.value.status_code == 400  # checks that deletion is blocked for active orders too
    assert "pending or active orders" in exc.value.detail.lower()  # checks the error message

def test_search_by_restaurant_name(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
        {"id": "r2", "name": "Burger Spot", "cuisine": "Fast Food", "address": "Kelowna"},
    ]
    fake_menu_items = []

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: fake_menu_items)

    results = restaurants_service.list_restaurants(keyword="Tokyo")

=======
>>>>>>> origin/main
    assert any(r.name == "Tokyo House" for r in results)


def test_search_by_menu_item(monkeypatch):
    fake_restaurants = [
        {"id": "7", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
<<<<<<< HEAD
        {"id": "r2", "name": "Burger Spot", "cuisine": "Fast Food", "address": "Kelowna"},
    ]
    fake_menu_items = [
        {
            "id": "m1",
            "restaurant_id": "7",
            "name": "Sushi",
            "price": 12.0,
            "order_qty": 1,
            "description": None,
        }
=======
    ]
    fake_menu_items = [
        {"id": "m1", "restaurant_id": "7", "name": "Sushi", "price": 12.0, "order_qty": 1}
>>>>>>> origin/main
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: fake_menu_items)

    results = restaurants_service.list_restaurants(keyword="sushi")

<<<<<<< HEAD
    assert len(results) > 0
=======
>>>>>>> origin/main
    assert any(r.id == "7" for r in results)


def test_search_is_case_insensitive(monkeypatch):
    fake_restaurants = [
        {"id": "7", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
    ]
<<<<<<< HEAD
    fake_menu_items = [
        {
            "id": "m1",
            "restaurant_id": "7",
            "name": "Sushi",
            "price": 12.0,
            "order_qty": 1,
            "description": None,
        }
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: fake_menu_items)
=======

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])
>>>>>>> origin/main

    lower = restaurants_service.list_restaurants(keyword="sushi")
    upper = restaurants_service.list_restaurants(keyword="SUSHI")

    assert lower == upper


def test_search_no_match(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
    ]
<<<<<<< HEAD
    fake_menu_items = []

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: fake_menu_items)
=======

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])
>>>>>>> origin/main

    results = restaurants_service.list_restaurants(keyword="xyznotfound")

    assert results == []


def test_search_with_cuisine_filter(monkeypatch):
    fake_restaurants = [
        {"id": "7", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
        {"id": "8", "name": "Sushi World", "cuisine": "Japanese", "address": "Vancouver"},
        {"id": "9", "name": "Burger Spot", "cuisine": "Fast Food", "address": "Kelowna"},
    ]
    fake_menu_items = [
<<<<<<< HEAD
        {
            "id": "m1",
            "restaurant_id": "7",
            "name": "Sushi",
            "price": 12.0,
            "order_qty": 1,
            "description": None,
        },
        {
            "id": "m2",
            "restaurant_id": "9",
            "name": "Sushi Burger",
            "price": 14.0,
            "order_qty": 1,
            "description": None,
        },
=======
        {"id": "m1", "restaurant_id": "7", "name": "Sushi", "price": 12.0, "order_qty": 1},
        {"id": "m2", "restaurant_id": "9", "name": "Sushi Burger", "price": 14.0, "order_qty": 1},
>>>>>>> origin/main
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: fake_menu_items)

    results = restaurants_service.list_restaurants(keyword="sushi", cuisine="Japanese")

<<<<<<< HEAD
    assert all(r.cuisine == "Japanese" for r in results)

def test_sort_by_rating(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "name": "A", "cuisine": "Indian", "address": "Kelowna", "rating": 4.2},
        {"id": "r2", "name": "B", "cuisine": "Indian", "address": "Kelowna", "rating": 4.8},
        {"id": "r3", "name": "C", "cuisine": "Indian", "address": "Kelowna", "rating": 3.9},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])

    results = restaurants_service.list_restaurants(sort_by="rating")

    assert [r.id for r in results] == ["r2", "r1", "r3"]

def test_sort_by_delivery_time(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "name": "A", "cuisine": "Indian", "address": "Vancouver", "rating": 4.2},
        {"id": "r2", "name": "B", "cuisine": "Indian", "address": "Kelowna", "rating": 4.8},
        {"id": "r3", "name": "C", "cuisine": "Indian", "address": "Victoria", "rating": 3.9},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])

    results = restaurants_service.list_restaurants(
        sort_by="delivery_time",
        customer_location="Kelowna"
    )

    assert [r.id for r in results] == ["r2", "r1", "r3"]

def test_sort_by_relevance(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "name": "Sushi House", "cuisine": "Japanese", "address": "Kelowna", "rating": 4.5},
        {"id": "r2", "name": "Tokyo Grill", "cuisine": "Japanese", "address": "Kelowna", "rating": 4.6},
    ]

    fake_menu_items = [
        {
            "id": "m1",
            "restaurant_id": "r2",
            "name": "Sushi Roll",
            "price": 12.0,
            "order_qty": 1,
            "description": None,
        }
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: fake_menu_items)

    results = restaurants_service.list_restaurants(keyword="sushi", sort_by="relevance")

    assert [r.id for r in results] == ["r1", "r2"]
=======
    assert all(r.cuisine == "Japanese" for r in results)
>>>>>>> origin/main
