<<<<<<< HEAD
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


DATA_PATH = Path(__file__).parent / "menu_items.json"


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


def get_discount_rate(promo_code: Optional[str]) -> float:
    promo_map = {
        "SAVE10": 0.10,
        "SAVE20": 0.20,
    }

    if not promo_code:
        return 0.0

    return promo_map.get(promo_code.upper(), 0.0)


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

        try:
            unit_price = float(menu_item["price"])
        except (KeyError, TypeError, ValueError):
            raise HTTPException(
                status_code=500,
                detail=f"Invalid price for menu item {ordered_item.menu_item_id}"
            )

        line_total = unit_price * ordered_item.quantity
        subtotal += line_total

        breakdown.append({
            "menu_item_id": ordered_item.menu_item_id,
            "name": menu_item.get("name", "Unknown Item"),
            "unit_price": round(unit_price, 2),
            "quantity": ordered_item.quantity,
            "line_total": round(line_total, 2)
        })

    discount_rate = get_discount_rate(order.promo_code)
    discount = subtotal * discount_rate
    discounted_subtotal = subtotal - discount

    service_charge = discounted_subtotal * order.service_charge_rate
    tax = discounted_subtotal * order.tax_rate
    total = discounted_subtotal + service_charge + tax + order.delivery_fee

    return {
        "items": breakdown,
        "subtotal": round(subtotal, 2),
        "promo_code": order.promo_code,
        "discount": round(discount, 2),
        "discounted_subtotal": round(discounted_subtotal, 2),
        "service_charge": round(service_charge, 2),
        "tax": round(tax, 2),
        "delivery_fee": round(order.delivery_fee, 2),
        "total": round(total, 2)
=======
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
    user_id: str
    items: List[OrderItem]
    promo_code: Optional[str] = None
    tax_rate: Optional[float] = Field(default=0.05, ge=0)
    delivery_fee: Optional[float] = Field(default=4.99, ge=0)
    service_charge_rate: Optional[float] = Field(default=0.10, ge=0)


DATA_PATH = Path(__file__).parent / "menu_items.json"


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


def get_discount_rate(promo_code: Optional[str]) -> float:
    promo_map = {
        "SAVE10": 0.10,
        "SAVE20": 0.20,
    }

    if not promo_code:
        return 0.0

    return promo_map.get(promo_code.upper(), 0.0)


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

        try:
            unit_price = float(menu_item["price"])
        except (KeyError, TypeError, ValueError):
            raise HTTPException(
                status_code=500,
                detail=f"Invalid price for menu item {ordered_item.menu_item_id}"
            )

        line_total = unit_price * ordered_item.quantity
        subtotal += line_total

        breakdown.append({
            "menu_item_id": ordered_item.menu_item_id,
            "name": menu_item.get("name", "Unknown Item"),
            "unit_price": round(unit_price, 2),
            "quantity": ordered_item.quantity,
            "line_total": round(line_total, 2)
        })

    discount_rate = get_discount_rate(order.promo_code)
    discount = subtotal * discount_rate
    discounted_subtotal = subtotal - discount

    service_charge = discounted_subtotal * order.service_charge_rate
    tax = discounted_subtotal * order.tax_rate
    total = discounted_subtotal + service_charge + tax + order.delivery_fee

    return {
        "items": breakdown,
        "subtotal": round(subtotal, 2),
        "promo_code": order.promo_code,
        "discount": round(discount, 2),
        "discounted_subtotal": round(discounted_subtotal, 2),
        "service_charge": round(service_charge, 2),
        "tax": round(tax, 2),
        "delivery_fee": round(order.delivery_fee, 2),
        "total": round(total, 2)
>>>>>>> 4e06249ccb96111f5e8a6411d771838c904027a8
    }