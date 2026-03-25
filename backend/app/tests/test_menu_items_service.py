import pytest
from fastapi import HTTPException

from app.services import menu_items_service
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate


def test_list_menu_items_for_restaurant_returns_matching_items(monkeypatch):
    fake_items = [
        {
            "id": "m1",
            "restaurant_id": "r1",
            "name": "Butter Chicken",
            "price": 15.5,
            "order_qty": 2,
            "description": "classic dish",
        },
        {
            "id": "m2",
            "restaurant_id": "r2",
            "name": "Tiramisu",
            "price": 8.0,
            "order_qty": 1,
            "description": "dessert",
        },
    ]

    monkeypatch.setattr(menu_items_service, "get_restaurant_by_id", lambda restaurant_id: {"id": restaurant_id})
    monkeypatch.setattr(menu_items_service, "load_all", lambda: fake_items)

    items = menu_items_service.list_menu_items_for_restaurant("r1")

    assert len(items) == 1
    assert items[0].name == "Butter Chicken"
    assert items[0].restaurant_id == "r1"


def test_create_menu_item_adds_new_item(monkeypatch):
    monkeypatch.setattr(menu_items_service, "get_restaurant_by_id", lambda restaurant_id: {"id": restaurant_id})
    monkeypatch.setattr(menu_items_service, "load_all", lambda: [])

    saved = {}
    monkeypatch.setattr(
        menu_items_service,
        "save_all",
        lambda items: saved.setdefault("items", items)
    )

    payload = MenuItemCreate(
        name="  Butter Chicken  ",
        price=15.5,
        order_qty=2,
        description=" classic dish "
    )

    item = menu_items_service.create_menu_item("r1", payload)

    assert item.restaurant_id == "r1"
    assert item.name == "Butter Chicken"
    assert item.description == "classic dish"
    assert len(saved["items"]) == 1
    assert saved["items"][0]["restaurant_id"] == "r1"


def test_create_menu_item_rejects_missing_restaurant(monkeypatch):
    def fake_get_restaurant_by_id(restaurant_id):
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")

    monkeypatch.setattr(menu_items_service, "get_restaurant_by_id", fake_get_restaurant_by_id)
    monkeypatch.setattr(menu_items_service, "load_all", lambda: [])
    monkeypatch.setattr(menu_items_service, "save_all", lambda items: None)

    payload = MenuItemCreate(
        name="Butter Chicken",
        price=15.5,
        order_qty=2,
        description=None
    )

    with pytest.raises(HTTPException) as exc:
        menu_items_service.create_menu_item("missing", payload)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


def test_create_menu_item_with_blank_name_raises_error(monkeypatch):
    monkeypatch.setattr(menu_items_service, "get_restaurant_by_id", lambda restaurant_id: {"id": restaurant_id})
    monkeypatch.setattr(menu_items_service, "load_all", lambda: [])
    monkeypatch.setattr(menu_items_service, "save_all", lambda items: None)

    payload = MenuItemCreate(
        name="   ",
        price=15.5,
        order_qty=2,
        description="classic dish"
    )

    with pytest.raises(HTTPException) as exc:
        menu_items_service.create_menu_item("r1", payload)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Menu item name cannot be empty."


def test_get_menu_item_by_id_returns_matching_item(monkeypatch):
    fake_items = [
        {
            "id": "m1",
            "restaurant_id": "r1",
            "name": "Butter Chicken",
            "price": 15.5,
            "order_qty": 2,
            "description": "classic dish",
        }
    ]

    monkeypatch.setattr(menu_items_service, "load_all", lambda: fake_items)

    item = menu_items_service.get_menu_item_by_id("m1")

    assert item.id == "m1"
    assert item.name == "Butter Chicken"


def test_get_menu_item_by_id_raises_404_when_missing(monkeypatch):
    monkeypatch.setattr(menu_items_service, "load_all", lambda: [])

    with pytest.raises(HTTPException) as exc:
        menu_items_service.get_menu_item_by_id("missing")

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


def test_update_menu_item_updates_existing_item(monkeypatch):
    fake_items = [
        {
            "id": "m1",
            "restaurant_id": "r1",
            "name": "Butter Chicken",
            "price": 15.5,
            "order_qty": 2,
            "description": "classic dish",
        }
    ]

    saved = {}

    monkeypatch.setattr(menu_items_service, "load_all", lambda: fake_items)
    monkeypatch.setattr(
        menu_items_service,
        "save_all",
        lambda items: saved.setdefault("items", items)
    )

    payload = MenuItemUpdate(
        name="  Butter Paneer  ",
        price=16.0,
        order_qty=3,
        description=" vegetarian option "
    )

    updated_item = menu_items_service.update_menu_item("m1", payload)

    assert updated_item.name == "Butter Paneer"
    assert updated_item.price == 16.0
    assert updated_item.order_qty == 3
    assert updated_item.description == "vegetarian option"
    assert saved["items"][0]["name"] == "Butter Paneer"


def test_update_menu_item_with_blank_name_raises_error(monkeypatch):
    fake_items = [
        {
            "id": "m1",
            "restaurant_id": "r1",
            "name": "Butter Chicken",
            "price": 15.5,
            "order_qty": 2,
            "description": "classic dish",
        }
    ]

    monkeypatch.setattr(menu_items_service, "load_all", lambda: fake_items)
    monkeypatch.setattr(menu_items_service, "save_all", lambda items: None)

    payload = MenuItemUpdate(
        name="   ",
        price=16.0,
        order_qty=3,
        description="vegetarian option"
    )

    with pytest.raises(HTTPException) as exc:
        menu_items_service.update_menu_item("m1", payload)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Menu item name cannot be empty."


def test_update_menu_item_raises_404_when_missing(monkeypatch):
    monkeypatch.setattr(menu_items_service, "load_all", lambda: [])
    monkeypatch.setattr(menu_items_service, "save_all", lambda items: None)

    payload = MenuItemUpdate(
        name="Butter Paneer",
        price=16.0,
        order_qty=3,
        description="vegetarian option"
    )

    with pytest.raises(HTTPException) as exc:
        menu_items_service.update_menu_item("missing", payload)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()

def test_delete_menu_item_removes_existing_item(monkeypatch):
    fake_items = [
        {
            "id": "m1",
            "restaurant_id": "r1",
            "name": "Butter Chicken",
            "price": 15.5,
            "order_qty": 2,
            "description": "classic dish",
        },
        {
            "id": "m2",
            "restaurant_id": "r1",
            "name": "Naan",
            "price": 3.5,
            "order_qty": 1,
            "description": "bread",
        },
    ]

    saved = {}

    monkeypatch.setattr(menu_items_service, "load_all", lambda: fake_items)
    monkeypatch.setattr(
        menu_items_service,
        "save_all",
        lambda items: saved.setdefault("items", items)
    )

    menu_items_service.delete_menu_item("m1")

    assert len(saved["items"]) == 1
    assert saved["items"][0]["id"] == "m2"


def test_delete_menu_item_raises_404_when_missing(monkeypatch):
    monkeypatch.setattr(menu_items_service, "load_all", lambda: [])
    monkeypatch.setattr(menu_items_service, "save_all", lambda items: None)

    with pytest.raises(HTTPException) as exc:
        menu_items_service.delete_menu_item("missing")

<<<<<<< HEAD
    assert exc.value.status_code == 404  # checks that deleting a missing item returns 404
    assert "not found" in exc.value.detail.lower()  # checks that the output is the expected error message
=======
    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()
>>>>>>> origin/main
