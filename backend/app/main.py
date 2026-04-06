from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from app.routers.restaurants import router as restaurants_router
from app.routers.menu_items import router as menu_items_router
from app.routers.data import router as data_router
from app.services.data_service import get_orders_from_csv
from app.routers.auth_router import router as auth_router
from app.routers.order_router import router as order_router
from app.routers.delivery_router import router as delivery_router
from app.routers.wallet import router as wallet_router
from app.schemas.order_schema import OrderItem
import httpx
import os

app = FastAPI(title="Backend Service")

PRICE_SERVICE = os.getenv("PRICE_URL", "http://price_service:8002")
NOTIFICATION_SERVICE = os.getenv("NOTIFICATION_URL", "http://notification_service:8001")




class OrderRequest(BaseModel):
    user_id: str
    items: List[OrderItem]
    promo_code: Optional[str] = None
    tax_rate: Optional[float] = Field(default=0.05, ge=0)
    delivery_fee: Optional[float] = Field(default=4.99, ge=0)
    service_charge_rate: Optional[float] = Field(default=0.10, ge=0)


@app.on_event("startup")
def startup_ingest():
    get_orders_from_csv()


@app.get("/")
def root():
    return {"message": "Backend running"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(restaurants_router)
app.include_router(menu_items_router)
app.include_router(data_router)
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(delivery_router)
app.include_router(wallet_router)