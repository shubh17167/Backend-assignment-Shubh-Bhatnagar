from app.storage import list_messages
import hmac
import hashlib
from fastapi import Request, HTTPException
from app.config import WEBHOOK_SECRET

from pydantic import BaseModel, Field
from typing import Optional
from app.storage import insert_message
from fastapi import FastAPI
from app.models import init_db

class WebhookMessage(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_: str = Field(..., alias="from")
    to: str = Field(..., min_length=1)
    ts: str
    text: Optional[str] = None


app = FastAPI()


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health/live")
def live():
    return {"status": "live"}


@app.get("/health/ready")
def ready():
    return {"status": "ready"}


def verify_signature(request_body: bytes, signature_header: str):
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="WEBHOOK_SECRET not set")

    computed = hmac.new(
        WEBHOOK_SECRET.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed, signature_header):
        raise HTTPException(status_code=401, detail="invalid signature")

@app.post("/webhook")
async def webhook(request: Request, message: WebhookMessage):
    signature = request.headers.get("X-Signature")

    if not signature:
        raise HTTPException(status_code=401, detail="invalid signature")

    body = await request.body()

    verify_signature(body, signature)

    inserted = insert_message(message.dict(by_alias=True))
    return {"status": "ok"}


@app.get("/messages")
def get_messages(
    limit: int = 10,
    offset: int = 0,
    from_: str | None = None,
    to: str | None = None,
):
    total, items = list_messages(
        limit=limit,
        offset=offset,
        from_msisdn=from_,
        to_msisdn=to,
    )

    return {
        "total": total,
        "items": items
    }
