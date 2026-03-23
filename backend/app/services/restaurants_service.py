import uuid
from typing import List
from fastapi import HTTPException
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.repositories.restaurants_repo import load_all, save_all
from app.repositories.orders_repo import has_unfinished_orders
from app.repositories.menu_items_repo import load_all as load_all_menu_items
from app.repositories.orders_repo import has_unfinished_orders


def matches_keyword(restaurant: Restaurant, keyword: str, menu_items: list[dict]) -> bool:
    keyword = keyword.lower().strip()

    if keyword in restaurant.name.lower():
        return True

    for item in menu_items:
        if item.get("restaurant_id") == restaurant.id:
            item_name = item.get("name", "")
            if keyword in item_name.lower():
                return True

    return False


def list_restaurants(
    location: str | None = None,
    cuisine: str | None = None,
    min_rating: float | None = None,
    keyword: str | None = None,
) -> List[Restaurant]:
    restaurants = [Restaurant(**r) for r in load_all()]

    if location:
        restaurants = [
            r for r in restaurants
            if r.address and location.lower() in r.address.lower()
        ]

    if cuisine:
        restaurants = [
            r for r in restaurants
            if r.cuisine and cuisine.lower() == r.cuisine.lower()
        ]

    if min_rating is not None:
        restaurants = [
            r for r in restaurants
            if getattr(r, "rating", None) is not None and r.rating >= min_rating
        ]

    if keyword:
        menu_items = load_all_menu_items()
        restaurants = [
            r for r in restaurants
            if matches_keyword(r, keyword, menu_items)
        ]

    return restaurants


def create_restaurant(payload: RestaurantCreate) -> Restaurant:
    restaurants = load_all()
    new_id = str(uuid.uuid4())

    if any(r.get("id") == new_id for r in restaurants):
        raise HTTPException(status_code=409, detail="ID collision; retry.")

    stripped_name = payload.name.strip()
    if not stripped_name:
        raise HTTPException(status_code=400, detail="Restaurant name cannot be empty.")

    new_restaurant = Restaurant(
        id=new_id,
        name=stripped_name,
        cuisine=payload.cuisine.strip() if payload.cuisine else None,
        address=payload.address.strip() if payload.address else None,
        rating=float(payload.rating) if getattr(payload, "rating", None) is not None else None,
    )
    restaurants.append(new_restaurant.dict())
    save_all(restaurants)
    return new_restaurant


def get_restaurant_by_id(restaurant_id: str) -> Restaurant:
    for r in load_all():
        if r.get("id") == restaurant_id:
            return Restaurant(**r)
    raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")


def update_restaurant(restaurant_id: str, payload: RestaurantUpdate) -> Restaurant:
    restaurants = load_all()

    for idx, r in enumerate(restaurants):
        if r.get("id") == restaurant_id:
            stripped_name = payload.name.strip()
            if not stripped_name:
                raise HTTPException(status_code=400, detail="Restaurant name cannot be empty.")

            updated = Restaurant(
                id=restaurant_id,
                name=stripped_name,
                cuisine=payload.cuisine.strip() if payload.cuisine else None,
                address=payload.address.strip() if payload.address else None,
                rating=float(payload.rating) if getattr(payload, "rating", None) is not None else None,
            )
            restaurants[idx] = updated.dict()
            save_all(restaurants)
            return updated

    raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")


def delete_restaurant(restaurant_id: str) -> None:
    restaurants = load_all()
    new_restaurants = [r for r in restaurants if r.get("id") != restaurant_id]
    save_all(new_restaurants)