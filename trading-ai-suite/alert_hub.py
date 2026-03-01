import os
import httpx
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlertHub")

app = FastAPI(title="Alert Hub Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Alert(BaseModel):
    source: str
    message: str
    severity: str  # 'INFO', 'WARNING', 'CRITICAL'
    payload: Optional[dict] = None

@app.post("/alerts")
async def receive_alert(alert: Alert):
    logger.info(f"Received alert from {alert.source}: {alert.message}")
    
    # 1. Discord Broadcast
    discord_url = os.getenv("DISCORD_WEBHOOK_URL")
    if discord_url:
        try:
            async with httpx.AsyncClient() as client:
                payload = {"content": f"🚨 **{alert.severity}** from {alert.source}\n{alert.message}"}
                await client.post(discord_url, json=payload)
        except Exception as e:
            logger.error(f"Discord fail: {e}")

    # 2. Telegram Broadcast
    tg_token = os.getenv("TELEGRAM_TOKEN")
    tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if tg_token and tg_chat_id:
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                payload = {"chat_id": tg_chat_id, "text": f"[{alert.severity}] {alert.source}: {alert.message}"}
                await client.post(url, json=payload)
        except Exception as e:
            logger.error(f"Telegram fail: {e}")

    return {"status": "broadcasted"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "alert-hub"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
