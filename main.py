from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal

app = FastAPI()

def NotificationRequest(Basemodel):
    user_id: str
    channel: Literal["email", "sms", "push"]
    messege: str
    subject: str | None=None

def NotificationResponse(Basemodel):
    notification_id: str
    status: str

@app.get("/health")
def health_check():
    return {"status":"ok"}




