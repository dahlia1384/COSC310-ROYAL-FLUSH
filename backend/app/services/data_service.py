import csv
import logging
from pathlib import Path
from typing import Any

from app.repositories.restaurants_repo import (
    load_all as load_restaurants,
    save_all as save_restaurants,
)
from app.repositories.menu_items_repo import (
    load_all as load_menu_items,
    save_all as save_menu_items,
)

REQUIRED_HEADERS = {
    "restaurant_id",
    "restaurant_name",
    "cuisine",
    "location",
    "food_item",
    "order_value",
    "order_qty",
}

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "food_delivery.csv"

logger = logging.getLogger(__name__)


def _clean_str(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _parse_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _validate_required_headers(fieldnames):
    actual_headers = set(fieldnames or [])
    missing_headers = REQUIRED_HEADERS - actual_headers
    if missing_headers:
        raise ValueError(f"CSV is missing required headers: {sorted(missing_headers)}")


def _build_menu_lookup(menu_items):
    menu_lookup = {}
    for item in menu_items:
        key = (_clean_str(item.get("restaurant_id")), _clean_str(item.get("name")))
        menu_lookup[key] = item
    return menu_lookup


def get_orders_from_csv():
    restaurants = load_restaurants()
    menu_items = load_menu_items()

    existing_restaurant_ids = {_clean_str(r.get("id")) for r in restaurants}
    menu_lookup = _build_menu_lookup(menu_items)

    restaurants_added = 0
    menu_items_added = 0
    menu_items_updated = 0
    rows_skipped = 0

    with DATA_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _validate_required_headers(reader.fieldnames)

        for line_number, row in enumerate(reader, start=2):
            restaurant_id = _clean_str(row.get("restaurant_id"))
            restaurant_name = _clean_str(row.get("restaurant_name"))
            cuisine = _clean_str(row.get("cuisine")) or None
            location = _clean_str(row.get("location")) or None
            food_item = _clean_str(row.get("food_item"))

            if not restaurant_id or not food_item:
                rows_skipped += 1
                logger.warning(
                    "Skipping row %s due to missing restaurant_id or food_item",
                    line_number,
                )
                continue

            raw_order_value = row.get("order_value")
            try:
                price = float(raw_order_value)
            except (TypeError, ValueError):
                rows_skipped += 1
                logger.warning(
                    "Skipping row %s due to invalid order_value '%s'",
                    line_number,
                    raw_order_value,
                )
                continue

            raw_order_qty = row.get("order_qty")
            try:
                order_qty = int(raw_order_qty)
            except (TypeError, ValueError):
                logger.warning(
                    "Invalid order_qty '%s' on row %s; defaulting to 1",
                    raw_order_qty,
                    line_number,
                )
                order_qty = 1

            if restaurant_id not in existing_restaurant_ids:
                restaurants.append(
                    {
                        "id": restaurant_id,
                        "name": restaurant_name,
                        "cuisine": cuisine,
                        "address": location,
                    }
                )
                existing_restaurant_ids.add(restaurant_id)
                restaurants_added += 1

            menu_key = (restaurant_id, food_item)

            if menu_key in menu_lookup:
                existing_item = menu_lookup[menu_key]
                existing_item["order_qty"] = int(existing_item.get("order_qty", 0)) + order_qty
                if price > 0:
                    existing_item["price"] = price
                menu_items_updated += 1
            else:
                new_item = {
                    "id": f"{restaurant_id}-{food_item.lower().replace(' ', '-')}",
                    "restaurant_id": restaurant_id,
                    "name": food_item,
                    "price": price,
                    "order_qty": order_qty,
                    "description": None,
                }
                menu_items.append(new_item)
                menu_lookup[menu_key] = new_item
                menu_items_added += 1

    save_restaurants(restaurants)
    save_menu_items(menu_items)

    logger.info(
        "CSV import complete: %s restaurants added, %s menu items added, %s menu items updated, %s rows skipped",
        restaurants_added,
        menu_items_added,
        menu_items_updated,
        rows_skipped,
    )

    return {
        "restaurants_added": restaurants_added,
        "menu_items_added": menu_items_added,
        "menu_items_updated": menu_items_updated,
        "rows_skipped": rows_skipped,
    }