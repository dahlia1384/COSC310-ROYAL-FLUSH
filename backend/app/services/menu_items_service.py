import uuid
from typing import List
from fastapi import HTTPException
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.repositories.menu_items_repo import load_all, save_all
from app.services.restaurants_service import get_restaurant_by_id

def assert_menu_item_owner(menu_item_id: str, owner_id: str) -> dict:
    items = load_all()
    for it in items:
        if it.get("id") == menu_item_id:
            restaurant = get_restaurant_by_id(it["restaurant_id"])
            if restaurant.get("owner_id") != owner_id:
                raise HTTPException(
                    status_code=403,
                    detail="You are not allowed to modify this menu item."
                )
            return it

    raise HTTPException(status_code=404, detail=f"Menu item '{menu_item_id}' not found")

def list_menu_items_for_restaurant(restaurant_id: str) -> List[MenuItem]:
    get_restaurant_by_id(restaurant_id)

    items = load_all()
    filtered = [it for it in items if it.get("restaurant_id") == restaurant_id]
    return [MenuItem(**it) for it in filtered]

def create_menu_item(restaurant_id: str, payload: MenuItemCreate, owner_id: str) -> MenuItem:
    restaurant = get_restaurant_by_id(restaurant_id)

    if restaurant.get("owner_id") != owner_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to add items to this restaurant."
        )

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
        description=payload.description.strip() if payload.description else None,
        available=payload.available,
    )

    items.append(new_item.dict())
    save_all(items)
    return new_item

def get_menu_item_by_id(menu_item_id: str) -> MenuItem:
    for it in load_all():
        if it.get("id") == menu_item_id:
            return MenuItem(**it)
    raise HTTPException(status_code=404, detail=f"Menu item '{menu_item_id}' not found")

def update_menu_item(menu_item_id: str, payload: MenuItemUpdate, owner_id: str) -> MenuItem:
    items = load_all()
    for idx, it in enumerate(items):
        if it.get("id") == menu_item_id:
            restaurant = get_restaurant_by_id(it["restaurant_id"])
            if restaurant.get("owner_id") != owner_id:
                raise HTTPException(
                    status_code=403,
                    detail="You are not allowed to modify this menu item."
                )
            stripped_name = payload.name.strip()
            if not stripped_name:
                raise HTTPException(status_code=400, detail="Menu item name cannot be empty.")

            updated = MenuItem(
                id=menu_item_id,
                restaurant_id=it["restaurant_id"],
                name=stripped_name,
                price=float(payload.price),
                description=payload.description.strip() if payload.description else None,
                available=payload.available,
            )

            items[idx] = updated.dict()
            save_all(items)
            return updated
    raise HTTPException(status_code=404, detail=f"Menu item '{menu_item_id}' not found")

def delete_menu_item(menu_item_id: str, owner_id: str) -> None:
    items = load_all()

    target = None
    for it in items:
        if it.get("id") == menu_item_id:
            target = it
            break

    if not target:
        raise HTTPException(status_code=404, detail=f"Menu item '{menu_item_id}' not found")

    restaurant = get_restaurant_by_id(target["restaurant_id"])
    if restaurant.get("owner_id") != owner_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this menu item."
        )

    new_items = [it for it in items if it.get("id") != menu_item_id]
    save_all(new_items)