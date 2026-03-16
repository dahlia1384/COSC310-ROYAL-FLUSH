from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.routers.restaurants import router as restaurants_router
from app.routers.menu_items import router as menu_items_router
from app.routers.data import router as data_router
from app.services.data_service import get_orders_from_csv
import httpx
import os

app = FastAPI(title="Backend Service")

PRICE_SERVICE = os.getenv("PRICE_URL", "http://price_service:8002")
NOTIFICATION_SERVICE = os.getenv("NOTIFICATION_URL", "http://notification_service:8001")


class Item(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    quantity: int = Field(..., gt=0)


class OrderRequest(BaseModel):
    user_id: int
    items: List[Item]


@app.get("/")
def root():
    return {"message": "Backend running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


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

    @app.on_event("startup")
    def startup_ingest():
        get_orders_from_csv()

    app.include_router(restaurants_router)
    app.include_router(menu_items_router)
    app.include_router(data_router)