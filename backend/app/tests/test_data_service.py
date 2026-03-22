import csv
from pathlib import Path
import pytest

from  app.services import data_service


def create_test_csv(tmp_path, headers, rows):
    # creates a temporary CSV file for testing.

    csv_path = tmp_path / "food_delivery.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as testFile:
        writer = csv.DictWriter(testFile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return csv_path


def patch_csv_path(monkeypatch, csv_path):
    # Replaces the DATA_PATH in data_service with this test CSV file so that the tests don't moify the real dataset.
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

    assert len(saved["restaurants"]) == 1 # checks tht only 1 restaurant was added
    assert saved["restaurants"][0]["name"] == "Spice House" # chcks that the added restaurant's name is correct (i.e is "Spice House")


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

    assert len(saved["menu"]) == 1 # checks that only 1 menu item was added
    assert saved["menu"][0]["name"] == "Mutter Paneer" # checks that the added menu item's name is correct (i.e is "Mutter Paneer")
    assert saved["menu"][0]["order_qty"] == 2 # checks that the added menu item's order quantity is correct (i.e is 2)


def test_updates_existing_menu_item_quantity(monkeypatch, tmp_path):
    # for this test I assumed that all orders were coming from the same location, customer, and during the same date/time frame. For example, a customer is ordering for a party and they keep changing their order quantiity as more people RSVP (before finalizing it) by adding more of the same item. So in that case, it would make sense to just update the order quantity of one order rather than creating a new order.

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

    assert saved["menu"][0]["order_qty"] == 10  # checks if the order quantity was updated correctly (i.e 5 + 2 + 3 = 10)


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

    assert saved["restaurants"] == [] # checks to make sure that no restaurants were added
    assert saved["menu"] == [] # checks to make sure that no menu items were added


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

    assert saved["restaurants"] == [] # checks to make sure that no restaurants were added
    assert saved["menu"] == [] # checks to make sure that no menu items were added



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

    assert saved["menu"][0]["order_qty"] == 1 # checks to make sure that the order quantity defaults to 1 when it's invalid


def test_missing_required_headers_raises_error(monkeypatch, tmp_path):

    headers = [
        "restaurant_id",
        "restaurant_name",
        "cuisine",
        "location",
        "food_item",
        # order_value is missing
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
        data_service.get_orders_from_csv() # checks that a missing required header causes a ValueError