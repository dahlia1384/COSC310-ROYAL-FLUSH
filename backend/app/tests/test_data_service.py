import csv
import pytest

from app.services import data_service


def create_test_csv(tmp_path, headers, rows):
    csv_path = tmp_path / "food_delivery.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as testFile:
        writer = csv.DictWriter(testFile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return csv_path


def patch_csv_path(monkeypatch, csv_path):
    monkeypatch.setattr(data_service, "DATA_PATH", csv_path)


BASE_ROW = {
    "restaurant_id": "r1",
    "restaurant_name": "Spice House",
    "cuisine": "Indian",
    "location": "Kelowna",
    "food_item": "Mutter Paneer",
    "order_value": "14.5",
    "order_qty": "2",
    "customer_rating": "4",
}


def run_import(monkeypatch, tmp_path, rows, headers=None):
    """Helper: write CSV, patch path, mock load/save, run import, return saved."""
    if headers is None:
        headers = rows[0].keys()
    csv_path = create_test_csv(tmp_path, headers, rows)
    patch_csv_path(monkeypatch, csv_path)

    saved = {}
    monkeypatch.setattr(data_service, "save_restaurants", lambda r: saved.update({"restaurants": r}))
    monkeypatch.setattr(data_service, "save_menu_items", lambda m: saved.update({"menu": m}))
    data_service.get_orders_from_csv()
    return saved


def test_adds_new_restaurant(monkeypatch, tmp_path):
    saved = run_import(monkeypatch, tmp_path, [BASE_ROW])
    assert len(saved["restaurants"]) == 1
    assert saved["restaurants"][0]["name"] == "Spice House"


def test_adds_new_menu_item(monkeypatch, tmp_path):
    saved = run_import(monkeypatch, tmp_path, [BASE_ROW])
    assert len(saved["menu"]) == 1
    assert saved["menu"][0]["name"] == "Mutter Paneer"
    assert saved["menu"][0]["price"] == round(14.5 / 2, 2)


def test_duplicate_menu_item_rows_only_create_one_item(monkeypatch, tmp_path):
    # Same dish appearing twice should still produce one menu item (first row wins for price)
    rows = [BASE_ROW, {**BASE_ROW, "order_value": "20.0", "order_qty": "4"}]
    saved = run_import(monkeypatch, tmp_path, rows)
    assert len(saved["menu"]) == 1
    assert saved["menu"][0]["price"] == round(14.5 / 2, 2)


def test_skips_rows_with_missing_required_fields(monkeypatch, tmp_path):
    rows = [
        {**BASE_ROW, "restaurant_id": ""},
        {**BASE_ROW, "restaurant_id": "r2", "food_item": ""},
    ]
    saved = run_import(monkeypatch, tmp_path, rows)
    assert saved["restaurants"] == []
    assert saved["menu"] == []


def test_invalid_order_value_skips_menu_item_but_keeps_restaurant(monkeypatch, tmp_path):
    # Restaurant is added before the menu item price is parsed, so it should still be saved
    rows = [{**BASE_ROW, "order_value": "invalid"}]
    saved = run_import(monkeypatch, tmp_path, rows)
    assert len(saved["restaurants"]) == 1
    assert saved["menu"] == []


def test_missing_required_headers_raises_error(monkeypatch, tmp_path):
    headers = ["restaurant_id", "restaurant_name", "cuisine", "location", "food_item", "order_qty"]
    rows = [{k: BASE_ROW[k] for k in headers}]
    csv_path = create_test_csv(tmp_path, headers, rows)
    patch_csv_path(monkeypatch, csv_path)
    monkeypatch.setattr(data_service, "save_restaurants", lambda r: None)
    monkeypatch.setattr(data_service, "save_menu_items", lambda m: None)
    with pytest.raises(ValueError):
        data_service.get_orders_from_csv()


def test_restaurant_rating_is_averaged(monkeypatch, tmp_path):
    rows = [
        {**BASE_ROW, "customer_rating": "4"},
        {**BASE_ROW, "food_item": "Dal Makhani", "order_value": "10", "customer_rating": "2"},
    ]
    saved = run_import(monkeypatch, tmp_path, rows)
    assert saved["restaurants"][0]["rating"] == 3.0


def test_missing_customer_rating_is_ignored(monkeypatch, tmp_path):
    rows = [
        {**BASE_ROW, "customer_rating": "4"},
        {**BASE_ROW, "food_item": "Dal Makhani", "order_value": "10", "customer_rating": ""},
    ]
    saved = run_import(monkeypatch, tmp_path, rows)
    assert saved["restaurants"][0]["rating"] == 4.0


def test_all_missing_ratings_gives_none(monkeypatch, tmp_path):
    rows = [{**BASE_ROW, "customer_rating": ""}]
    saved = run_import(monkeypatch, tmp_path, rows)
    assert saved["restaurants"][0]["rating"] is None