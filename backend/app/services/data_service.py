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


def _build_menu_lookup(menu_items: list[dict]) -> dict[tuple[str, str], dict]:
    lookup = {}
    for item in menu_items:
        key = (_clean_str(item.get("restaurant_id")), _clean_str(item.get("name")))
        lookup[key] = item
    return lookup


def _validate_headers(fieldnames: list[str] | None) -> None:
    required = {
        "restaurant_id",
        "restaurant_name",
        "cuisine",
        "location",
        "food_item",
        "order_value",
        "order_qty",
    }

    actual = set(fieldnames or [])
    missing = required - actual
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")


def get_orders_from_csv() -> dict[str, int]:
    """
    Read food delivery order data from the CSV file and update the
    restaurant and menu item JSON datasets.

    Returns:
        dict[str, int]: Summary of how many restaurants were added,
        menu items were added, and existing menu items were updated.
    """
    logger.info("Starting food delivery CSV import from %s", DATA_PATH)

    restaurants = load_restaurants()
    menu_items = load_menu_items()
REQUIRED_HEADERS = {
    "restaurant_id",
    "restaurant_name",
    "cuisine",
    "location",
    "food_item",
    "order_value",
    "order_qty",
}


def _validate_required_headers(fieldnames):
    # Raises a ValueError if the CSV is missing any required column headers

    actual_headers = set(fieldnames or [])
    missing_headers = REQUIRED_HEADERS - actual_headers
    if missing_headers:
        raise ValueError(f"CSV is missing required headers: {sorted(missing_headers)}")


    existing_restaurant_ids = {_clean_str(r.get("id")) for r in restaurants}
    menu_lookup = _build_menu_lookup(menu_items)
def _build_menu_lookup(menu_items):
    # builds a lookup dictionary to keep track of existing recorded orders for each menu item 

    restaurants_added = 0
    menu_items_added = 0
    menu_items_updated = 0
    rows_skipped = 0
    menu_lookup = {}
    for item in menu_items:
        key = (str(item["restaurant_id"]).strip(), str(item["name"]).strip())
        menu_lookup[key] = item
    return menu_lookup


def get_orders_from_csv():
    # Reads orders from the CSV file and then updates the appropriate JSON files accordingly

    restaurants = load_restaurants()
    menu_items = load_menu_items()

    existing_restaurant_ids = {str(r["id"]).strip() for r in restaurants}
    menu_lookup = _build_menu_lookup(menu_items)

    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _validate_headers(reader.fieldnames)
        _validate_required_headers(reader.fieldnames)

        for line_number, row in enumerate(reader, start=2):
            restaurant_id = _clean_str(row.get("restaurant_id"))
            restaurant_name = _clean_str(row.get("restaurant_name"))
            cuisine = _clean_str(row.get("cuisine")) or None
            location = _clean_str(row.get("location")) or None
            food_item = _clean_str(row.get("food_item"))

        for row in reader:
            line_number = reader.line_num

            restaurant_id = str(row["restaurant_id"]).strip()
            restaurant_name = str(row["restaurant_name"]).strip()
            cuisine = str(row["cuisine"]).strip() if row["cuisine"] else None
            location = str(row["location"]).strip() if row["location"] else None
            food_item = str(row["food_item"]).strip()
            
            if not restaurant_id or not food_item:
                rows_skipped += 1
                logger.warning(
                    "Skipping row %s due to missing restaurant_id or food_item",
                    line_number,
                )
                print(f"Error on row {line_number}: missing restaurant_id or food_item. Row skipped. Please fix and try again.")
                continue

            price = _parse_float(row.get("order_value"), 0.0)
            order_qty = _parse_int(row.get("order_qty"), 0)
            try:
                price = float(row["order_value"])
            except (ValueError, TypeError):
                print(f"Error on row {line_number}: invalid order_value '{row['order_value']}'. Row skipped.")
                continue

            try:
                order_qty = int(row["order_qty"])
            except (ValueError, TypeError):
                print(f"Warning on row {line_number}: invalid order_qty '{row['order_qty']}'. Defaulting to 1.")
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
                restaurants.append({
                    "id": restaurant_id,
                    "name": restaurant_name,
                    "cuisine": cuisine,
                    "address": location,
                })
                existing_restaurant_ids.add(restaurant_id)
                restaurants_added += 1

            menu_key = (restaurant_id, food_item)

            if menu_key in menu_lookup:
                existing_item = menu_lookup[menu_key]
                existing_item["order_qty"] = int(existing_item.get("order_qty", 0)) + order_qty

                existing_item["order_qty"] = existing_item.get("order_qty", 0) + order_qty
                if price > 0:
                    existing_item["price"] = price
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
                    "description": None,
                }
                menu_items.append(new_item)
                menu_lookup[menu_key] = new_item

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
    return 0
