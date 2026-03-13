from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import json
from pathlib import Path

app = FastAPI(title="Price Service")


class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0)


class OrderRequest(BaseModel):
    user_id: int
    items: List[OrderItem]
    tax_rate: Optional[float] = Field(default=0.05, ge=0)
    delivery_fee: Optional[float] = Field(default=4.99, ge=0)


DATA_PATH = Path("/app/data/menu_items.json")


@app.get("/")
def root():
    return {"message": "Price service running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


def load_menu_items():
    if not DATA_PATH.exists():
        raise HTTPException(status_code=500, detail="menu_items.json not found")

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="menu_items.json is invalid")

    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="menu_items.json must contain a list")

    return data


def build_menu_lookup(menu_items):
    lookup = {}

    for item in menu_items:
        item_id = item.get("id")
        name = item.get("name")
        price = item.get("price")

        if item_id is None or name is None or price is None:
            continue

        try:
            lookup[int(item_id)] = {
                "id": int(item_id),
                "name": str(name),
                "price": float(price)
            }
        except (TypeError, ValueError):
            continue

    return lookup


@app.post("/calculate")
def calculate_price(order: OrderRequest):
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    menu_items = load_menu_items()
    menu_lookup = build_menu_lookup(menu_items)

    subtotal = 0.0
    item_breakdown = []

    for ordered_item in order.items:
        menu_item = menu_lookup.get(ordered_item.menu_item_id)

        if not menu_item:
            raise HTTPException(
                status_code=404,
                detail=f"Menu item {ordered_item.menu_item_id} not found"
            )

        unit_price = menu_item["price"]
        quantity = ordered_item.quantity
        line_total = unit_price * quantity
        subtotal += line_total

        item_breakdown.append({
            "menu_item_id": menu_item["id"],
            "name": menu_item["name"],
            "unit_price": round(unit_price, 2),
            "quantity": quantity,
            "line_total": round(line_total, 2)
        })

    tax = subtotal * order.tax_rate
    total = subtotal + tax + order.delivery_fee

    return {
        "items": item_breakdown,
        "subtotal": round(subtotal, 2),
        "tax_rate": round(order.tax_rate, 4),
        "tax": round(tax, 2),
        "delivery_fee": round(order.delivery_fee, 2),
        "total": round(total, 2)
    }
