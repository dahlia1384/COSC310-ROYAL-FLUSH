import csv
from pathlib import Path
import pytest

from  app.services import data_service


def create_test_csv(tmp_path, headers, rows):
    csv_path = tmp_path / "food_delivery.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as testFile:
        writer = csv.DictWriter(testFile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return csv_path


def patch_csv_path(monkeypatch, csv_path):
    monkeypatch.setattr(data_service, "DATA_PATH", csv_path)


def test_adds_new_restaurant(monkeypatch, tmp_path):
    rows = [{
        "restaurant_id": "r1",
        "restaurant_name": "Spice House",
        "cuisine": "Indian",
        "location": "Kelowna",
        "food_item": "Mutter Paneer",
        "order_value": "14.5",
        "order_qty": "2",
    }]

    csv_path = create_test_csv(tmp_path, rows[0].keys(), rows)
    patch_csv_path(monkeypatch, csv_path)

    monkeypatch.setattr(data_service, "load_restaurants", lambda: [])
    monkeypatch.setattr(data_service, "load_menu_items", lambda: [])

    saved = {}
    monkeypatch.setattr(data_service, "save_restaurants", lambda r: saved.setdefault("restaurants", r))
    monkeypatch.setattr(data_service, "save_menu_items", lambda m: saved.setdefault("menu", m))

    data_service.get_orders_from_csv()

    assert len(saved["restaurants"]) == 1
    assert saved["restaurants"][0]["name"] == "Spice House"


def test_adds_new_menu_item(monkeypatch, tmp_path):
    rows = [{
        "restaurant_id": "r1",
        "restaurant_name": "Spice House",
        "cuisine": "Indian",
        "location": "Kelowna",
        "food_item": "Mutter Paneer",
        "order_value": "14.5",
        "order_qty": "2",
    }]

    csv_path = create_test_csv(tmp_path, rows[0].keys(), rows)
    patch_csv_path(monkeypatch, csv_path)

    monkeypatch.setattr(data_service, "load_restaurants", lambda: [])
    monkeypatch.setattr(data_service, "load_menu_items", lambda: [])

    saved = {}
    monkeypatch.setattr(data_service, "save_restaurants", lambda r: None)
    monkeypatch.setattr(data_service, "save_menu_items", lambda m: saved.setdefault("menu", m))

    data_service.get_orders_from_csv()

    assert len(saved["menu"]) == 1
    assert saved["menu"][0]["name"] == "Mutter Paneer"
    assert saved["menu"][0]["order_qty"] == 2


def test_updates_existing_menu_item_quantity(monkeypatch, tmp_path):
    rows = [
        {
            "restaurant_id": "r1",
            "restaurant_name": "Spice House",
            "cuisine": "Indian",
            "location": "Kelowna",
            "food_item": "Mutter Paneer",
            "order_value": "14.5",
            "order_qty": "2",
        },
        {
            "restaurant_id": "r1",
            "restaurant_name": "Spice House",
            "cuisine": "Indian",
            "location": "Kelowna",
            "food_item": "Mutter Paneer",
            "order_value": "14.5",
            "order_qty": "3",
        },
    ]

    csv_path = create_test_csv(tmp_path, rows[0].keys(), rows)
    patch_csv_path(monkeypatch, csv_path)

    existing_menu = [{
        "id": "r1-mutter-paneer",
        "restaurant_id": "r1",
        "name": "Mutter Paneer",
        "price": 10,
        "order_qty": 5,
        "description": None
    }]

    monkeypatch.setattr(data_service, "load_restaurants", lambda: [])
    monkeypatch.setattr(data_service, "load_menu_items", lambda: existing_menu)

    saved = {}
    monkeypatch.setattr(data_service, "save_restaurants", lambda r: None)
    monkeypatch.setattr(data_service, "save_menu_items", lambda m: saved.setdefault("menu", m))

    data_service.get_orders_from_csv()

    assert saved["menu"][0]["order_qty"] == 10


def test_skips_rows_with_missing_required_fields(monkeypatch, tmp_path):
    rows = [
        {
            "restaurant_id": "",
            "restaurant_name": "Roma Nord Bistro",
            "cuisine": "Italian",
            "location": "Kelowna",
            "food_item": "Carbonara",
            "order_value": "10",
            "order_qty": "1",
        },
        {
            "restaurant_id": "r2",
            "restaurant_name": "Roma Nord Bistro",
            "cuisine": "Italian",
            "location": "Kelowna",
            "food_item": "",
            "order_value": "10",
            "order_qty": "1",
        },
    ]

    csv_path = create_test_csv(tmp_path, rows[0].keys(), rows)
    patch_csv_path(monkeypatch, csv_path)

    monkeypatch.setattr(data_service, "load_restaurants", lambda: [])
    monkeypatch.setattr(data_service, "load_menu_items", lambda: [])

    saved = {}
    monkeypatch.setattr(data_service, "save_restaurants", lambda r: saved.setdefault("restaurants", r))
    monkeypatch.setattr(data_service, "save_menu_items", lambda m: saved.setdefault("menu", m))

    data_service.get_orders_from_csv()

    assert saved["restaurants"] == []
    assert saved["menu"] == []


def test_invalid_order_value_row_is_skipped(monkeypatch, tmp_path):

    rows = [{
        "restaurant_id": "r2",
        "restaurant_name": "Roma Nord Bistro",
        "cuisine": "Italian",
        "location": "Kelowna",
        "food_item": "Tiramisu",
        "order_value": "invalid",
        "order_qty": "2",
    }]

    csv_path = create_test_csv(tmp_path, rows[0].keys(), rows)
    patch_csv_path(monkeypatch, csv_path)

    monkeypatch.setattr(data_service, "load_restaurants", lambda: [])
    monkeypatch.setattr(data_service, "load_menu_items", lambda: [])

    saved = {}

    monkeypatch.setattr(data_service, "save_restaurants",
        lambda r: saved.setdefault("restaurants", r))

    monkeypatch.setattr(data_service, "save_menu_items",
        lambda m: saved.setdefault("menu", m))

    data_service.get_orders_from_csv()

    assert saved["restaurants"] == []
    assert saved["menu"] == []



def test_invalid_order_qty_defaults_to_one(monkeypatch, tmp_path):

    rows = [{
        "restaurant_id": "r2",
        "restaurant_name": "Roma Nord Bistro",
        "cuisine": "Italian",
        "location": "Kelowna",
        "food_item": "Tiramisu",
        "order_value": "10",
        "order_qty": "invalid",
    }]

    csv_path = create_test_csv(tmp_path, rows[0].keys(), rows)
    patch_csv_path(monkeypatch, csv_path)

    monkeypatch.setattr(data_service, "load_restaurants", lambda: [])
    monkeypatch.setattr(data_service, "load_menu_items", lambda: [])

    saved = {}
    monkeypatch.setattr(data_service, "save_restaurants", lambda r: None)
    monkeypatch.setattr(data_service, "save_menu_items", lambda m: saved.setdefault("menu", m))

    data_service.get_orders_from_csv()

    assert saved["menu"][0]["order_qty"] == 1


def test_missing_required_headers_raises_error(monkeypatch, tmp_path):

    headers = [
        "restaurant_id",
        "restaurant_name",
        "cuisine",
        "location",
        "food_item",
        "order_qty"
    ]

    rows = [{
        "restaurant_id": "r2",
        "restaurant_name": "Roma Nord Bistro",
        "cuisine": "Italian",
        "location": "Kelowna",
        "food_item": "Carbonara",
        "order_qty": "2",
    }]

    csv_path = create_test_csv(tmp_path, headers, rows)
    patch_csv_path(monkeypatch, csv_path)

    monkeypatch.setattr(data_service, "load_restaurants", lambda: [])
    monkeypatch.setattr(data_service, "load_menu_items", lambda: [])

    monkeypatch.setattr(data_service, "save_restaurants", lambda r: None)
    monkeypatch.setattr(data_service, "save_menu_items", lambda m: None)

    with pytest.raises(ValueError):
<<<<<<< HEAD
        data_service.get_orders_from_csv() # checks that a missing required header causes a ValueError
=======
        data_service.get_orders_from_csv()
>>>>>>> origin/main
