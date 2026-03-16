from pydantic import BaseModel
from  datetime import datetime

class OrderCreate(BaseModel):
    order_id: str
    restaurant_id: int
    customer_id: str #change customer_id data type to UUID
    food_item: str
    order_qty: int

class Order(BaseModel):
    order_id: str
    restaurant_id: int
    customer_id: str #change customer_id data type to UUID
    food_item: str
    order_qty: int
    order_status: str
    order_time: datetime

class OrderStatusUpdate(BaseModel):
    order_status: str


    


