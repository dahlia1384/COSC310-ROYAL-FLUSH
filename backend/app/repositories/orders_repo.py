from pathlib import Path
import json, os
from typing import List, Dict, Any
from datetime import datetime

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "orders.json"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_all(orders: List[Dict[str, Any]]) -> None:
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)

def has_unfinished_orders(restaurant_id: str) -> bool:
    unfinished_statuses = {"Order Created", "Preparing Order", "Order Out for Delivery"}
<<<<<<< HEAD

=======
>>>>>>> origin/main
    for order in load_all():
        if (
            order.get("restaurant_id") == restaurant_id
            and order.get("order_status", "") in unfinished_statuses
        ):
            return True

    return False

def create_order(order_data: Dict[str, Any]) -> Dict[str, Any]: 
    orders = load_all()
    order_data["order_time"] = datetime.utcnow().isoformat()
    orders.append(order_data)
    save_all(orders)
    return order_data

def get_order_by_id(order_id: str) -> Dict[str, Any]:
    for order in load_all():
        if order.get("order_id") == order_id:
            return order
    return None

def get_orders_by_customer(customer_id: str) -> List[Dict[str, Any]]:
    return [o for o in load_all() if str(o.get("customer_id")) == str(customer_id)]

def update_order_status(order_id: str, new_status: str) -> Dict[str, Any]:
    orders = load_all()
    for order in orders:
        if order.get("order_id") == order_id:
            order["order_status"]=new_status
            save_all(orders)
            return order
    return None
<<<<<<< HEAD
       
=======
>>>>>>> origin/main
