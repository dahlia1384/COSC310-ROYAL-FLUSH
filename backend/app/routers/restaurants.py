from fastapi import APIRouter, status, Query, Depends
from typing import List
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.services.auth_dependencies import require_role
from app.services.restaurants_service import (
    list_restaurants as list_restaurants_service,
    create_restaurant as create_restaurant_service,
    get_restaurant_by_id as get_restaurant_by_id_service,
    update_restaurant as update_restaurant_service,
    delete_restaurant as delete_restaurant_service,
)

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("", response_model=List[Restaurant])
def get_restaurants(
    location: str | None = None,
    cuisine: str | None = None,
    min_rating: float | None = Query(default=None, ge=0, le=5),
       keyword: str | None = None,
    sort_by: str = Query(default="relevance", pattern="^(relevance|rating|delivery_time)$"),
    customer_location: str | None = None
):
    return list_restaurants_service(
        location=location,
        cuisine=cuisine,
        min_rating=min_rating,
        keyword=keyword,
        sort_by=sort_by,
        customer_location=customer_location
    ) 

@router.post("", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    payload: RestaurantCreate,
    current_user=Depends(require_role("RESTAURANT_OWNER"))
):
    return create_restaurant_service(payload, owner_id=current_user.id)

@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str):
    return get_restaurant_by_id_service(restaurant_id)

@router.put("/{restaurant_id}", response_model=Restaurant)
def update_restaurant(
    restaurant_id: str,
    payload: RestaurantUpdate,
    current_user=Depends(require_role("RESTAURANT_OWNER"))
):
    return update_restaurant_service(restaurant_id, payload, owner_id=current_user.id)

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: str,
    current_user=Depends(require_role("RESTAURANT_OWNER"))
):
    delete_restaurant_service(restaurant_id, owner_id=current_user.id)
    return None