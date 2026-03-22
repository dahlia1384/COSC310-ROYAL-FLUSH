from pydantic import BaseModel, Field
from typing import List
from  datetime import datetime
from uuid import UUID

class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    restaurant_id: int
    customer_id: UUID
    items: List[OrderItem]

class Order(BaseModel):
    order_id: str
    restaurant_id: int
    customer_id: UUID
    items: List[OrderItem]
    order_status: str
    order_time: datetime

class OrderStatusUpdate(BaseModel):
    order_status: str = Field(min_length=1)




