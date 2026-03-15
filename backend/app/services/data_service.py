import csv
from pathlib import Path

from app.repositories.restaurants_repo import load_all as load_restaurants, save_all as save_restaurants
from app.repositories.menu_items_repo import load_all as load_menu_items, save_all as save_menu_items

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "food_delivery.csv"

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


def _build_menu_lookup(menu_items):
    # builds a lookup dictionary to keep track of existing recorded orders for each menu item 

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
        _validate_required_headers(reader.fieldnames)

        for row in reader:
            line_number = reader.line_num

            restaurant_id = str(row["restaurant_id"]).strip()
            restaurant_name = str(row["restaurant_name"]).strip()
            cuisine = str(row["cuisine"]).strip() if row["cuisine"] else None
            location = str(row["location"]).strip() if row["location"] else None
            food_item = str(row["food_item"]).strip()
            
            if not restaurant_id or not food_item:
                print(f"Error on row {line_number}: missing restaurant_id or food_item. Row skipped. Please fix and try again.")
                continue

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
                restaurants.append({
                    "id": restaurant_id,
                    "name": restaurant_name,
                    "cuisine": cuisine,
                    "address": location,
                })
                existing_restaurant_ids.add(restaurant_id)

            menu_key = (restaurant_id, food_item)

            if menu_key in menu_lookup:
                existing_item = menu_lookup[menu_key]
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

    save_restaurants(restaurants)
    save_menu_items(menu_items)

    return 0
