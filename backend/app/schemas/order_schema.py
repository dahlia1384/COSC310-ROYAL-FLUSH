from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime
from uuid import UUID

class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    restaurant_id: int
    customer_id: UUID
    items: List[OrderItem]

    @validator("items")
    def validate_items_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError("items must contain at least one item")
        return v

class Order(BaseModel):
    order_id: str
    restaurant_id: int
    customer_id: UUID
    items: List[OrderItem]
    order_status: str
    order_time: datetime

class OrderStatusUpdate(BaseModel):
    order_status: str = Field(min_length=1)