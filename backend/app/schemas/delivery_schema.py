from pydantic import BaseModel, Field
from datetime import datetime

class Delivery(BaseModel):
    order_id: str
    restaurant_id: int
    delivery_status: str
    delivery_method: str
    delivery_time: datetime

class DeliveryStatusUpdate(BaseModel):
    delivery_status: str = Field(min_length=1)
