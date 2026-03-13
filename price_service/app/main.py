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
    promo_code: Optional[str] = None
    tax_rate: Optional[float] = Field(default=0.05, ge=0)
    delivery_fee: Optional[float] = Field(default=4.99, ge=0)
    service_charge_rate: Optional[float] = Field(default=0.10, ge=0)


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

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/calculate")
def calculate_price(order: OrderRequest):
    menu_items = load_menu_items()
    menu_lookup = {item["id"]: item for item in menu_items if "id" in item}

    subtotal = 0.0
    breakdown = []

    for ordered_item in order.items:
        menu_item = menu_lookup.get(ordered_item.menu_item_id)

        if not menu_item:
            raise HTTPException(
                status_code=404,
                detail=f"Menu item {ordered_item.menu_item_id} not found"
            )

        unit_price = float(menu_item["price"])
        line_total = unit_price * ordered_item.quantity
        subtotal += line_total

        breakdown.append({
            "menu_item_id": ordered_item.menu_item_id,
            "name": menu_item["name"],
            "unit_price": round(unit_price, 2),
            "quantity": ordered_item.quantity,
            "line_total": round(line_total, 2)
        })

    service_charge = subtotal * order.service_charge_rate

    discount = 0.0
    if order.promo_code == "SAVE10":
        discount = subtotal * 0.10
    elif order.promo_code == "SAVE20":
        discount = subtotal * 0.20

    subtotal_after_discount = subtotal - discount
    tax = subtotal_after_discount * order.tax_rate
    total = subtotal_after_discount + tax + order.delivery_fee + service_charge

    return {
        "items": breakdown,
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "service_charge": round(service_charge, 2),
        "tax": round(tax, 2),
        "delivery_fee": round(order.delivery_fee, 2),
        "total": round(total, 2)
    }
