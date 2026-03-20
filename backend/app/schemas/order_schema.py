from pydantic import BaseModel,Field
from  datetime import datetime
from uuid import UUID

class OrderCreate(BaseModel):
    order_id: str
    restaurant_id: int
    customer_id: UUID
    food_item: str = Field(min_length=1)
    order_qty: int = Field(gt=0)

class Order(BaseModel):
    order_id: str
    restaurant_id: int
    customer_id: UUID
    food_item: str
    order_qty: int
    order_status: str
    order_time: datetime

class OrderStatusUpdate(BaseModel):
    order_status: str = Field(min_length=1)


    


