from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Price service running"}

@app.post("/calculate")
def calculate_price(order: dict):
    items = order.get("items", [])
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax = subtotal * 0.05
    delivery_fee = 4.99
    total = subtotal + tax + delivery_fee

    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "delivery_fee": delivery_fee,
        "total": round(total, 2)
    }
