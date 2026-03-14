from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Notification Service")


class NotificationRequest(BaseModel):
    user_id: int
    message: str = Field(..., min_length=1)


@app.get("/")
def root():
    return {"message": "Notification service running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/send")
def send_notification(data: NotificationRequest):
    return {
        "status": "notification sent",
        "data": data.model_dump()
    }
