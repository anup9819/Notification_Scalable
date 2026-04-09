from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
import redis 
import uuid

app = FastAPI()
redis_client = redis.Redis(host="localhost",port= 6379, decode_responses=True)

#the messege user wantes to send 
class NotificationRequest(BaseModel):
    user_id: str
    channel: Literal["email", "sms", "push"]
    message: str
    subject: str | None=None

#the reponse the user will get after sending the messege
class NotificationResponse(BaseModel):
    notification_id: str
    status: str
    message: str

def check_rate_limit(user_id : str):
    key = f"rate limit:{user_id}"
    count = redis_client.incr(key)
    if count==1:
        redis_client.expire(key,60)
    if count>5:
        raise HTTPException(
            status_code=409,
            detail=f"rate limit exceeded. max 5 tries per 60 seconds."
        )

@app.get("/health")
def health_check():
    return {"status":"ok"}

#sending notification
@app.post("/notify",response_model=NotificationResponse)
def send_notification(payload: NotificationRequest):
    check_rate_limit(payload.user_id)
    notification_id = str(uuid.uuid4())
    
    redis_client.setex(
        f"notification:{notification_id}",
        3600,
        "queued"
    )

    return NotificationResponse(
        notification_id=notification_id,
        status = "queued",
        message=f"Notification with id: {notification_id}, is queued for {payload.channel} for user {payload.user_id}."
    )

@app.get("/notify/{notification_id}/status")
def get_status(notification_id: str):
    status = redis_client.get(f"notification:{notification_id}")
    if not status:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"notification_id": notification_id, "status": status}





