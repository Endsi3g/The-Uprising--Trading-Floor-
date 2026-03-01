import os
import json
import httpx
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional

# Configuration
INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", 500.0))
ALERT_HUB_URL = os.getenv("ALERT_HUB_URL", "http://alert-hub:8005/alerts")

# Risk Constants
MAX_DAILY_LOSS_PCT = 0.02
MAX_TRADE_LOSS_PCT = 0.01
CIRCUIT_BREAKER_PCT = 0.05
COOLDOWN_HOURS = 4

class RiskEngine:
    def __init__(self, initial_capital=500.0):
        self.capital = initial_capital
        self.daily_start_capital = initial_capital
        self.current_loss = 0.0
        self.is_halted = False
        self.cooldown_until: Optional[datetime] = None
        self.consecutive_losses = 0
        self.trade_history = []

    async def send_alert(self, message: str, severity: str = "WARNING"):
        """Broadcast alert to Alert Hub."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(ALERT_HUB_URL, json={
                    "source": "RiskEngine",
                    "message": message,
                    "severity": severity
                })
        except Exception as e:
            print(f"Alert Hub unreachable: {e}")

    async def check_trade_safety(self, symbol: str, side: str, amount: float, current_pnl: float):
        if self.is_halted:
            return False, "⚠️ CIRCUIT BREAKER ACTIVE"

        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return False, "🕒 COOLDOWN ACTIVE"

        daily_loss_limit = self.daily_start_capital * MAX_DAILY_LOSS_PCT
        if self.current_loss >= daily_loss_limit:
            self.is_halted = True
            msg = f"MAX DAILY LOSS REACHED: {self.current_loss}$"
            await self.send_alert(msg, "CRITICAL")
            return False, f"❌ {msg}"

        if current_pnl < -(self.capital * MAX_TRADE_LOSS_PCT):
            self.consecutive_losses += 1
            if self.consecutive_losses >= 3:
                self.trigger_cooldown()
                await self.send_alert("3 consecutive losses. Cooldown activated.", "WARNING")
            return False, f"⚠️ STOP LOSS TRIGGERED ({current_pnl}$)"

        self.trade_history.append({
            "symbol": symbol, "side": side, "amount": amount, "pnl": current_pnl,
            "timestamp": datetime.now().isoformat()
        })
        return True, "✅ Risk Validation Passed"

    def trigger_cooldown(self):
        self.cooldown_until = datetime.now() + timedelta(hours=COOLDOWN_HOURS)
        self.consecutive_losses = 0

    def reset_daily(self):
        self.daily_start_capital = self.capital
        self.current_loss = 0.0
        self.is_halted = False

    def get_status(self) -> dict:
        return {
            "capital": self.capital,
            "is_halted": self.is_halted,
            "cooldown_active": bool(self.cooldown_until and datetime.now() < self.cooldown_until),
            "recent_trades": self.trade_history[-5:]
        }

engine = RiskEngine(initial_capital=INITIAL_CAPITAL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🛡️ Risk Engine online (Capital: ${engine.capital})")
    await engine.send_alert("Risk Engine has started and is monitoring the floor.", "INFO")
    yield
    print("👋 Risk Engine offline")

app = FastAPI(title="Risk Engine API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class TradeCheckRequest(BaseModel):
    symbol: str
    side: str
    amount: float
    current_pnl: float

@app.get("/health")
async def health():
    return {"status": "ok", "service": "risk-engine", "is_halted": engine.is_halted}

@app.get("/risk/status")
async def get_risk_status():
    return engine.get_status()

@app.post("/risk/check")
async def check_trade(req: TradeCheckRequest):
    allowed, message = await engine.check_trade_safety(req.symbol, req.side, req.amount, req.current_pnl)
    return {"allowed": allowed, "message": message}

@app.post("/risk/reset")
async def reset_daily_risk():
    engine.reset_daily()
    return {"status": "reset"}
