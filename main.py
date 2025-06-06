from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SHOP_ID = os.getenv("SHOP_ID")
SHOP_TOKEN = os.getenv("SHOP_TOKEN")

class PaymentRequest(BaseModel):
    telegram_id: str

@app.post("/create-payment")
async def create_payment(data: PaymentRequest):
    idempotence_key = str(uuid.uuid4())
    headers = {
        "Authorization": f"Bearer {SHOP_TOKEN}",
        "Idempotence-Key": idempotence_key,
        "Content-Type": "application/json"
    }
    payload = {
        "amount": {"value": "299.00", "currency": "RUB"},
        "confirmation": {
            "type": "embedded",
            "return_url": "https://t.me/your_bot?start=paid"
        },
        "capture": True,
        "description": f"Сказака — подписка для {data.telegram_id}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.yookassa.ru/v3/payments",
            json=payload,
            headers=headers,
            auth=(SHOP_ID, SHOP_TOKEN)
        )
    resp_json = response.json()
    return {
        "id": resp_json["id"],
        "confirmation_token": resp_json["confirmation"]["confirmation_token"]
    }
