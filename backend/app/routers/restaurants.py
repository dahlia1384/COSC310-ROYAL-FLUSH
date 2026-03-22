from fastapi import APIRouter, status
from typing import List
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.services.restaurants_service import (
    list_restaurants,
    create_restaurant,
    get_restaurant_by_id,
    update_restaurant,
    delete_restaurant,
)

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("", response_model=List[Restaurant])
def get_restaurants(
    location: str | None = None,
    cuisine: str | None = None,
    min_rating: float | None = Query(default=None, ge=0, le=5)
):
    return list_restaurants(
        location=location,
        cuisine=cuisine,
        min_rating=min_rating
    )

@router.post("", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
def create_restaurant(payload: RestaurantCreate):
    return create_restaurant(payload)

@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str):
    return get_restaurant_by_id(restaurant_id)

@router.put("/{restaurant_id}", response_model=Restaurant)
def update_restaurant(restaurant_id: str, payload: RestaurantUpdate):
    return update_restaurant(restaurant_id, payload)

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(restaurant_id: str):
    delete_restaurant(restaurant_id)
    return None