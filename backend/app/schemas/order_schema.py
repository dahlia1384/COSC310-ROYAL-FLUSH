from pydantic import BaseModel
from typing import List
from  datetime import datetime

class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    restaurant_id: int
    items: List[OrderItem]

class Order(BaseModel):
    id: int
    user_id: int
    restaraunt_id: int
    items: List[OrderItem]
    status: str
    created_at: datetime

class OrderStatusUpdate(BaseModel):
    status: str

class OrderResponse(BaseModel):
    d: int
    user_id: int
    restaraunt_id: int
    status: str
    created_at: datetime
    


