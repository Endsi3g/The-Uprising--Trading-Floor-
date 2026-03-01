import os
import httpx
import logging
import asyncio
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

async def broadcast_discord(alert: Alert):
    discord_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not discord_url:
        return
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}.get(alert.severity, "🔔")
        payload = {
            "content": f"{emoji} **{alert.severity}** from `{alert.source}`\n> {alert.message}"
        }
        try:
            resp = await client.post(discord_url, json=payload)
            resp.raise_for_status()
            logger.info(f"Discord broadcast success for {alert.source}")
        except Exception as e:
            logger.error(f"Discord broadcast failed: {e}")

async def broadcast_telegram(alert: Alert):
    tg_token = os.getenv("TELEGRAM_TOKEN")
    tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not (tg_token and tg_chat_id):
        return
    
    url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}.get(alert.severity, "🔔")
    text = f"{emoji} [{alert.severity}] {alert.source}\n{alert.message}"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(url, json={"chat_id": tg_chat_id, "text": text})
            resp.raise_for_status()
            logger.info(f"Telegram broadcast success for {alert.source}")
        except Exception as e:
            logger.error(f"Telegram broadcast failed: {e}")

@app.post("/alerts")
async def receive_alert(alert: Alert, background_tasks: BackgroundTasks):
    logger.info(f"Incoming alert: [{alert.severity}] {alert.source}: {alert.message}")
    
    # Broadcast in background to avoid blocking the caller
    background_tasks.add_task(broadcast_discord, alert)
    background_tasks.add_task(broadcast_telegram, alert)
    
    return {"status": "queued", "source": alert.source}

@app.post("/test-alert")
async def test_alert(background_tasks: BackgroundTasks):
    """Utility endpoint to verify connectivity."""
    test_alert = Alert(
        source="AlertHub-Internal",
        message="System connectivity test. If you see this, broadcasting is working.",
        severity="INFO"
    )
    background_tasks.add_task(broadcast_discord, test_alert)
    background_tasks.add_task(broadcast_telegram, test_alert)
    return {"status": "test_queued"}

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "service": "alert-hub",
        "discord_configured": bool(os.getenv("DISCORD_WEBHOOK_URL")),
        "telegram_configured": bool(os.getenv("TELEGRAM_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
