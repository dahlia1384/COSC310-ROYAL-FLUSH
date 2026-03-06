from fastapi import FastAPI
from routers.restaurants import router as restaurants_router
from routers.menu_items import router as menu_items_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(restaurants_router)
app.include_router(menu_items_router)
