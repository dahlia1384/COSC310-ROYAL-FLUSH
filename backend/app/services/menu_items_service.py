import uuid
from typing import List
from fastapi import HTTPException
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.repositories.menu_items_repo import load_all, save_all
from app.services.restaurants_service import get_restaurant_by_id

def list_menu_items_for_restaurant(restaurant_id: str) -> List[MenuItem]:
    get_restaurant_by_id(restaurant_id)

    items = load_all()
    filtered = [it for it in items if it.get("restaurant_id") == restaurant_id]
    return [MenuItem(**it) for it in filtered]

def create_menu_item(restaurant_id: str, payload: MenuItemCreate) -> MenuItem:
    get_restaurant_by_id(restaurant_id)

    items = load_all()
    new_id = str(uuid.uuid4())
    if any(it.get("id") == new_id for it in items):
        raise HTTPException(status_code=409, detail="ID collision; retry.")

    stripped_name = payload.name.strip()
    if not stripped_name:
        raise HTTPException(status_code=400, detail="Menu item name cannot be empty.")

    new_item = MenuItem(
        id=new_id,
        restaurant_id=restaurant_id,
        name=stripped_name,
        price=float(payload.price),
        order_qty=int(payload.order_qty),
        description=payload.description.strip() if payload.description else None
    )
    items.append(new_item.dict())
    save_all(items)
    return new_item

def get_menu_item_by_id(menu_item_id: str) -> MenuItem:
    for it in load_all():
        if it.get("id") == menu_item_id:
            return MenuItem(**it)
    raise HTTPException(status_code=404, detail=f"Menu item '{menu_item_id}' not found")

def update_menu_item(menu_item_id: str, payload: MenuItemUpdate) -> MenuItem:
    items = load_all()
    for idx, it in enumerate(items):
        if it.get("id") == menu_item_id:
            stripped_name = payload.name.strip()
            if not stripped_name:
                raise HTTPException(status_code=400, detail="Menu item name cannot be empty.")

            updated = MenuItem(
                id=menu_item_id,
                restaurant_id=it["restaurant_id"],
                name=stripped_name,
                price=float(payload.price),
                order_qty=int(payload.order_qty),
                description=payload.description.strip() if payload.description else None
            )
            items[idx] = updated.dict()
            save_all(items)
            return updated
    raise HTTPException(status_code=404, detail=f"Menu item '{menu_item_id}' not found")

def delete_menu_item(menu_item_id: str) -> None:
    items = load_all()
    new_items = [it for it in items if it.get("id") != menu_item_id]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail=f"Menu item '{menu_item_id}' not found")
    save_all(new_items)