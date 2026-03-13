from fastapi import APIRouter
from app.services.data_service import get_orders_from_csv

router = APIRouter(prefix="/orders", tags=["data"])

@router.post("/food-delivery")
def food_delivery():
    return get_orders_from_csv()