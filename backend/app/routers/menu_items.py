from fastapi import APIRouter, status
from typing import List
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.services.menu_items_service import (
    list_menu_items_for_restaurant,
    create_menu_item,
    get_menu_item_by_id,
    update_menu_item,
    delete_menu_item,
)

router = APIRouter(tags=["menu-items"])

@router.get("/restaurants/{restaurant_id}/menu-items", response_model=List[MenuItem])
def get_menu_items(restaurant_id: str):
    return list_menu_items_for_restaurant(restaurant_id)

@router.post("/restaurants/{restaurant_id}/menu-items", response_model=MenuItem, status_code=status.HTTP_201_CREATED)
def post_menu_item(restaurant_id: str, payload: MenuItemCreate):
    return create_menu_item(restaurant_id, payload)

@router.get("/menu-items/{menu_item_id}", response_model=MenuItem)
def get_menu_item(menu_item_id: str):
    return get_menu_item_by_id(menu_item_id)

@router.put("/menu-items/{menu_item_id}", response_model=MenuItem)
def put_menu_item(menu_item_id: str, payload: MenuItemUpdate):
    return update_menu_item(menu_item_id, payload)

@router.delete("/menu-items/{menu_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_menu_item(menu_item_id: str):
    delete_menu_item(menu_item_id)
    return None