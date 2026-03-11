from fastapi import FastAPI
from app.routers.restaurants import router as restaurants_router
from app.routers.menu_items import router as menu_items_router
from app.routers.data import router as data_router
from app.services.data_service import get_orders_from_csv
import httpx
import os

app = FastAPI()

PRICE_SERVICE = os.getenv("PRICE_URL", "http://price_service:8002")
NOTIFICATION_SERVICE = os.getenv("NOTIFICATION_URL", "http://notification_service:8001")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Backend running"}

@app.post("/place-order")
async def place_order(order: dict):
    async with httpx.AsyncClient() as client:
        price_response = await client.post(
            f"{PRICE_SERVICE}/calculate",
            json=order
        )
        price_data = price_response.json()

        await client.post(
            f"{NOTIFICATION_SERVICE}/send",
            json={
                "user_id": order.get("user_id"),
                "message": f"Your order total is ${price_data['total']}"
            }
        )

    return {
        "status": "order processed",
        "pricing": price_data
    }

@app.on_event("startup")
def startup_ingest():
    get_orders_from_csv()

app.include_router(restaurants_router)
app.include_router(menu_items_router)
app.include_router(data_router)