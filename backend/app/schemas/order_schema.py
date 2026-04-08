from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class OrderItem(BaseModel):
    menu_item_id: str
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    restaurant_id: str
    customer_id: str
    items: List[OrderItem]
    delivery_method: str
    customer_city: str

    @validator("items")
    def validate_items_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError("items must contain at least one item")
        return v

class Order(BaseModel):
    order_id: str
    restaurant_id: str
    customer_id: str
    items: List[OrderItem]
    order_status: str
    order_time: datetime
    total: Optional[float] = None
    delivery_method: str
    customer_city: str
    
class OrderStatusUpdate(BaseModel):
    order_status: str = Field(min_length=1)