from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Notification service running"}

@app.post("/send")
def send_notification(data: dict):
    return {
        "status": "notification sent",
        "data": data
    }
