from fastapi import FastAPI
from app.routers.restaurants import router as restaurants_router
from app.routers.menu_items import router as menu_items_router
from app.routers.data import router as data_router
from app.services.data_service import get_orders_from_csv

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def startup_ingest():
    get_orders_from_csv()

app.include_router(restaurants_router)
app.include_router(menu_items_router)
app.include_router(data_router)