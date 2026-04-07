import csv
import logging
from pathlib import Path
from typing import Any

from app.repositories.restaurants_repo import save_all as save_restaurants
from app.repositories.menu_items_repo import save_all as save_menu_items


REQUIRED_HEADERS = {
    "restaurant_id",
    "restaurant_name",
    "cuisine",
    "location",
    "food_item",
    "order_value",
    "order_qty",
    "customer_rating"
}

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "food_delivery.csv"

logger = logging.getLogger(__name__)


def _clean_str(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _validate_required_headers(fieldnames):
    actual_headers = set(fieldnames or [])
    missing_headers = REQUIRED_HEADERS - actual_headers
    if missing_headers:
        raise ValueError(f"CSV is missing required headers: {sorted(missing_headers)}")


def get_orders_from_csv():
    restaurants = {}
    restaurant_ratings = {}
    menu_items = {}
    rows_skipped = 0

    with DATA_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _validate_required_headers(reader.fieldnames)

        for line_number, row in enumerate(reader, start=2):
            restaurant_id = _clean_str(row.get("restaurant_id"))
            food_item = _clean_str(row.get("food_item"))

            if not restaurant_id or not food_item:
                rows_skipped += 1
                logger.warning("Skipping row %s due to missing restaurant_id or food_item", line_number)
                continue

            if restaurant_id not in restaurants:
                restaurants[restaurant_id] = {
                    "id": restaurant_id,
                    "owner_id": f"seed-owner-{restaurant_id}",
                    "name": _clean_str(row.get("restaurant_name")),
                    "cuisine": _clean_str(row.get("cuisine")) or None,
                    "address": _clean_str(row.get("location")) or None,
                    "rating": None,
                }
                restaurant_ratings[restaurant_id] = []

            raw_rating = row.get("customer_rating")
            if raw_rating is not None and _clean_str(raw_rating) != "":
                try:
                    restaurant_ratings[restaurant_id].append(float(raw_rating))
                except (TypeError, ValueError):
                    logger.warning("Invalid customer_rating '%s' on row %s; skipping rating", raw_rating, line_number)

            menu_item_id = f"{restaurant_id}-{food_item.lower().replace(' ', '-')}"
            if menu_item_id not in menu_items:
                try:
                    order_value = float(row.get("order_value"))
                    order_qty = int(row.get("order_qty"))
                except Exception:
                    rows_skipped += 1
                    logger.warning("Skipping row %s due to invalid order_qty", line_number)
                    continue

                if order_qty <= 0:
                    rows_skipped += 1
                    logger.warning("Skipping row %s due to invalid order_qty", line_number)
                    continue

                menu_items[menu_item_id] = {
                    "id": menu_item_id,
                    "restaurant_id": restaurant_id,
                    "name": food_item,
                    "price": round(order_value / order_qty, 2),
                    "description": None,
                }

    for restaurant_id, ratings in restaurant_ratings.items():
        if ratings:
            restaurants[restaurant_id]["rating"] = round(sum(ratings) / len(ratings), 2)

    save_restaurants(list(restaurants.values()))
    save_menu_items(list(menu_items.values()))

    logger.info(
        "CSV import complete: %s restaurants, %s menu items, %s rows skipped",
        len(restaurants),
        len(menu_items),
        rows_skipped,
    )

    return {
        "restaurants_added": len(restaurants),
        "menu_items_added": len(menu_items),
        "rows_skipped": rows_skipped,
    }