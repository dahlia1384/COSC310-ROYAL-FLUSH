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


@app.post("/place-order")
async def place_order(order: OrderRequest):

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:

            # call price service
            price_response = await client.post(
                f"{PRICE_SERVICE}/calculate",
                json=order.model_dump()
            )
            price_response.raise_for_status()
            price_data = price_response.json()

            # send notification
            await client.post(
                f"{NOTIFICATION_SERVICE}/send",
                json={
                    "user_id": order.user_id,
                    "message": f"Your order total is ${price_data['total']}"
                }
            )

        return {
            "message": "Full cost breakdown before payment",
            "cost_breakdown": {
                "subtotal": price_data["subtotal"],
                "tax": price_data["tax"],
                "delivery_fee": price_data["delivery_fee"],
                "total": price_data["total"]
            }
        }

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Service unavailable")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")

app.include_router(restaurants_router)
app.include_router(menu_items_router)
app.include_router(data_router)
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(delivery_router)
