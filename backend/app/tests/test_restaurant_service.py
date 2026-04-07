import pytest
from fastapi import HTTPException
from app.services import restaurants_service
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate


def test_list_restaurants_returns_all_restaurants(monkeypatch: pytest.MonkeyPatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-1", "name": "Spice House", "cuisine": "Indian", "address": "123 Main St"},
        {"id": "r2", "owner_id": "owner-2", "name": "Roma Nord Bistro", "cuisine": "Italian", "address": "456 Oak Ave"},
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

    restaurant = restaurants_service.create_restaurant(payload, owner_id="owner-1")

    assert restaurant.name == "Spice House"
    assert restaurant.cuisine == "Indian"
    assert restaurant.address == "123 Main St"
    assert restaurant.owner_id == "owner-1"
    assert len(saved["restaurants"]) == 1
    assert saved["restaurants"][0]["owner_id"] == "owner-1"

def test_update_restaurant_allows_owner(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-1", "name": "Spice House", "cuisine": "Indian", "address": "123 Main St", "rating": 4.2}
    ]

    saved = {}
    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(
        restaurants_service,
        "save_all",
        lambda restaurants: saved.setdefault("restaurants", restaurants)
    )

    payload = RestaurantUpdate( name="  New Spice House ", cuisine=" Indian ", address=" 999 Updated Ave ", rating=4.8)

    updated = restaurants_service.update_restaurant("r1", payload, owner_id="owner-1")

    assert updated.id == "r1"
    assert updated.owner_id == "owner-1"
    assert updated.name == "New Spice House"
    assert updated.address == "999 Updated Ave"
    assert saved["restaurants"][0]["owner_id"] == "owner-1"


def test_update_restaurant_blocks_non_owner(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-1", "name": "Spice House", "cuisine": "Indian", "address": "123 Main St", "rating": 4.2,}
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    payload = RestaurantUpdate( name="New Spice House", cuisine="Indian", address="999 Updated Ave", rating=4.8)

    with pytest.raises(HTTPException) as exc:
        restaurants_service.update_restaurant("r1", payload, owner_id="owner-2")

    assert exc.value.status_code == 403
    assert "not allowed" in exc.value.detail.lower()

def test_delete_restaurant_when_missing_raises_404(monkeypatch):
    monkeypatch.setattr(restaurants_service, "load_all", lambda: [])
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    with pytest.raises(HTTPException) as exc:
        restaurants_service.delete_restaurant("missing", owner_id="owner-1")

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


def test_delete_restaurant_with_pending_orders_raises_400(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-1", "name": "Spice House", "cuisine": "Indian", "address": "123 Main St"}
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "has_unfinished_orders", lambda restaurant_id: True)
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    with pytest.raises(HTTPException) as exc:
        restaurants_service.delete_restaurant("r1", owner_id="owner-1")

    assert exc.value.status_code == 400
    assert "pending or active orders" in exc.value.detail.lower()

def test_delete_restaurant_blocks_non_owner(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-1", "name": "Spice House", "cuisine": "Indian",
            "address": "123 Main St"}
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "has_unfinished_orders", lambda restaurant_id: False)
    monkeypatch.setattr(restaurants_service, "save_all", lambda restaurants: None)

    with pytest.raises(HTTPException) as exc:
        restaurants_service.delete_restaurant("r1", owner_id="owner-2")

    assert exc.value.status_code == 403
    assert "not allowed" in exc.value.detail.lower()


def test_delete_restaurant_allows_owner(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-1", "name": "Spice House", "cuisine": "Indian",
            "address": "123 Main St"},
        {"id": "r2", "owner_id": "owner-2", "name": "Roma Nord Bistro", "cuisine": "Italian", "address": "456 Oak Ave"}
    ]

    saved = {}
    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "has_unfinished_orders", lambda restaurant_id: False)
    monkeypatch.setattr(
        restaurants_service,
        "save_all",
        lambda restaurants: saved.setdefault("restaurants", restaurants)
    )

    restaurants_service.delete_restaurant("r1", owner_id="owner-1")

    assert len(saved["restaurants"]) == 1
    assert saved["restaurants"][0]["id"] == "r2"

def test_search_by_restaurant_name(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-1", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
        {"id": "r2", "owner_id": "owner-2", "name": "Burger Spot", "cuisine": "Fast Food", "address": "Kelowna"},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])

    results = restaurants_service.list_restaurants(keyword="Tokyo")

    assert any(r.name == "Tokyo House" for r in results)


def test_search_by_menu_item(monkeypatch):
    fake_restaurants = [
        {"id": "7", "owner_id": "owner-1", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
    ]
    fake_menu_items = [
        {"id": "m1", "restaurant_id": "7", "name": "Sushi", "price": 12.0}
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: fake_menu_items)

    results = restaurants_service.list_restaurants(keyword="sushi")

    assert any(r.id == "7" for r in results)


def test_search_is_case_insensitive(monkeypatch):
    fake_restaurants = [
        {"id": "7", "owner_id": "owner-1", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])

    lower = restaurants_service.list_restaurants(keyword="sushi")
    upper = restaurants_service.list_restaurants(keyword="SUSHI")

    assert lower == upper


def test_search_no_match(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-1", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])

    results = restaurants_service.list_restaurants(keyword="xyznotfound")

    assert results == []


def test_search_with_cuisine_filter(monkeypatch):
    fake_restaurants = [
        {"id": "7", "owner_id": "owner-1", "name": "Tokyo House", "cuisine": "Japanese", "address": "Kelowna"},
        {"id": "8", "owner_id": "owner-2", "name": "Sushi World", "cuisine": "Japanese", "address": "Vancouver"},
        {"id": "9", "owner_id": "owner-3", "name": "Burger Spot", "cuisine": "Fast Food", "address": "Kelowna"},
    ]
    fake_menu_items = [
        {"id": "m1", "restaurant_id": "7", "name": "Sushi", "price": 12.0},
        {"id": "m2", "restaurant_id": "9", "name": "Sushi Burger", "price": 14.0},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: fake_menu_items)

    results = restaurants_service.list_restaurants(keyword="sushi", cuisine="Japanese")

    assert all(r.cuisine == "Japanese" for r in results)

def test_sort_by_rating(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-4", "name": "A", "cuisine": "Indian", "address": "Kelowna", "rating": 4.2},
        {"id": "r2", "owner_id": "owner-5", "name": "B", "cuisine": "Indian", "address": "Kelowna", "rating": 4.8},
        {"id": "r3", "owner_id": "owner-6", "name": "C", "cuisine": "Indian", "address": "Kelowna", "rating": 3.9},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])

    results = restaurants_service.list_restaurants(sort_by="rating")

    assert [r.id for r in results] == ["r2", "r1", "r3"]

def test_sort_by_delivery_time(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-4", "name": "A", "cuisine": "Indian", "address": "City_5", "rating": 4.2},
        {"id": "r2", "owner_id": "owner-5", "name": "B", "cuisine": "Indian", "address": "City_2", "rating": 4.8},
        {"id": "r3", "owner_id": "owner-6", "name": "C", "cuisine": "Indian", "address": "City_8", "rating": 3.9},
    ]

    monkeypatch.setattr(restaurants_service, "load_all", lambda: fake_restaurants)
    monkeypatch.setattr(restaurants_service, "load_all_menu_items", lambda: [])

    results = restaurants_service.list_restaurants(
        sort_by="delivery_time",
        customer_location="City_2"
    )

    assert [r.id for r in results] == ["r2", "r1", "r3"]

def test_sort_by_relevance(monkeypatch):
    fake_restaurants = [
        {"id": "r1", "owner_id": "owner-7", "name": "Sushi House", "cuisine": "Japanese", "address": "Kelowna", "rating": 4.5},
        {"id": "r2", "owner_id": "owner-8", "name": "Tokyo Grill", "cuisine": "Japanese", "address": "Kelowna", "rating": 4.6},
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