from pydantic import BaseModel
from datetime import datetime

class DeliveryCreate(BaseModel):
    delivery_id: str
    
