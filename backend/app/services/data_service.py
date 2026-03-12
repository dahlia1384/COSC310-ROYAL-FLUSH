import csv
from pathlib import Path

from app.repositories.restaurants_repo import load_all as load_restaurants, save_all as save_restaurants
from app.repositories.menu_items_repo import load_all as load_menu_items, save_all as save_menu_items

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "food_delivery.csv"

def get_orders_from_csv():
    # Read all orders from the CSV and update the appropriate JSON files accordingly.
    restaurants = load_restaurants()
    menu_items = load_menu_items()

    existing_restaurant_ids = {r["id"] for r in restaurants}
    existing_menu_keys = {(m["restaurant_id"], m["name"]) for m in menu_items}

    menu_lookup = {}
    for item in menu_items:
        key = (str(item["restaurant_id"]).strip(), str(item["name"]).strip())
        menu_lookup[key] = item

    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            restaurant_id = str(row["restaurant_id"]).strip()
            restaurant_name = str(row["restaurant_name"]).strip()
            cuisine = str(row["cuisine"]).strip() if row["cuisine"] else None
            location = str(row["location"]).strip() if row["location"] else None
            food_item = str(row["food_item"]).strip()

            if not restaurant_id or not food_item:
                continue

            try:
                price = float(row["order_value"])
            except (ValueError, TypeError):
                price = 0.0

            try:
                order_qty = int(row["order_qty"])
            except (ValueError, TypeError):
                order_qty = 0

            if restaurant_id not in existing_restaurant_ids:
                restaurants.append({
                    "id": restaurant_id,
                    "name": restaurant_name,
                    "cuisine": cuisine,
                    "address": location
                })
                existing_restaurant_ids.add(restaurant_id)

            menu_key = (restaurant_id, food_item)

            if menu_key in menu_lookup:
                existing_item = menu_lookup[menu_key]
                existing_item["order_qty"] = existing_item.get("order_qty", 0) + order_qty

                if price > 0:
                    existing_item["price"] = price


            else:
                menu_items.append({
                    "id": f"{restaurant_id}-{food_item.lower().replace(' ', '-')}",
                    "restaurant_id": restaurant_id,
                    "name": food_item,
                    "price": price,
                    "order_qty": order_qty,
                    "description": None
                })
                existing_menu_keys.add(menu_key)

    save_restaurants(restaurants)
    save_menu_items(menu_items)

    return 0