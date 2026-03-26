from pathlib import Path
import json, os
from typing import List, Dict, Any
from datetime import datetime

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "deliveries.json"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_all(deliveries: List[Dict[str, Any]]) -> None:
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(deliveries, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)

def create_delivery(delivery_data: Dict[str, Any]) -> Dict[str, Any]: 
    deliveries = load_all()
    delivery_data["delivery_time"] = datetime.utcnow().isoformat()
    deliveries.append(delivery_data)
    save_all(deliveries)
    return delivery_data

def get_delivery_by_order_id(delivery_id: str) -> Dict[str, Any]:
    for delivery in load_all():
        if delivery.get("order_id") == order_id:
            return delivery
    return None

def update_delivery_status(order_id: str, new_status: str) -> Dict[str, Any]:
    deliveries = load_all()
    for delivery in deliveries:
        if delivery.get("order_id") == order_id:
            delivery["delivery_status"]=new_status
            save_all(deliveries)
            return delivery
    return None




       
