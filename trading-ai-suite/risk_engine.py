import os
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional

# Risk Constants (Based on Aggressive Profile with Guardrails)
MAX_DAILY_LOSS_PCT = 0.02   # 2% ($100 on $5000 total / $10 on $500 live)
MAX_TRADE_LOSS_PCT = 0.01   # 1% ($5 on $500 live)
CIRCUIT_BREAKER_PCT = 0.05  # 5% ($25 on $500 live) 24h total
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

    def check_trade_safety(self, symbol: str, side: str, amount: float, current_pnl: float):
        """Valide si un trade respecte les limites avant execution."""

        # 1. Check Circuit Breaker
        if self.is_halted:
            return False, "⚠️ CIRCUIT BREAKER ACTIVE: Trading halted."

        # 2. Check Cooldown
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            remaining = (self.cooldown_until - datetime.now()).seconds // 60
            return False, f"🕒 COOLDOWN ACTIVE: {remaining}m remaining."

        # 3. Daily Loss Protection
        daily_loss_limit = self.daily_start_capital * MAX_DAILY_LOSS_PCT
        if self.current_loss >= daily_loss_limit:
            self.is_halted = True
            return False, f"❌ MAX DAILY LOSS REACHED: {self.current_loss}$ >= {daily_loss_limit}$"

        # 4. Individual Trade Loss Protection
        if current_pnl < -(self.capital * MAX_TRADE_LOSS_PCT):
            self.consecutive_losses += 1
            if self.consecutive_losses >= 3:
                self.trigger_cooldown()
            return False, f"⚠️ STOP LOSS TRIGGERED: Trade PnL too low ({current_pnl}$)"

        # 5. Record trade
        self.trade_history.append({
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "pnl": current_pnl,
            "timestamp": datetime.now().isoformat()
        })

        return True, "✅ Risk Validation Passed."

    def trigger_cooldown(self):
        """Active un cooldown obligatoire de 4h."""
        self.cooldown_until = datetime.now() + timedelta(hours=COOLDOWN_HOURS)
        self.consecutive_losses = 0
        print(f"🛑 3 PERTES CONSECUTIVES: Cooldown de {COOLDOWN_HOURS}h activé.")

    def reset_daily(self):
        """Reset les compteurs au debut de la journée."""
        self.daily_start_capital = self.capital
        self.current_loss = 0.0
        self.is_halted = False
        print("🌅 Daily Risk Reset.")

    def get_status(self) -> dict:
        """Retourne l'état complet du Risk Engine."""
        return {
            "capital": self.capital,
            "daily_start_capital": self.daily_start_capital,
            "current_loss": self.current_loss,
            "is_halted": self.is_halted,
            "cooldown_until": self.cooldown_until.isoformat() if self.cooldown_until else None,
            "consecutive_losses": self.consecutive_losses,
            "max_daily_loss_pct": MAX_DAILY_LOSS_PCT,
            "max_trade_loss_pct": MAX_TRADE_LOSS_PCT,
            "circuit_breaker_pct": CIRCUIT_BREAKER_PCT,
            "cooldown_hours": COOLDOWN_HOURS,
            "recent_trades": self.trade_history[-10:]  # Last 10 trades
        }


# --- FastAPI Wrapper ---
engine = RiskEngine(initial_capital=float(os.getenv("INITIAL_CAPITAL", "500.0")))


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🛡️ Risk Engine starting with capital: ${engine.capital}")
    yield
    print("👋 Risk Engine shutting down.")


app = FastAPI(title="Risk Engine API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TradeCheckRequest(BaseModel):
    symbol: str
    side: str
    amount: float
    current_pnl: float


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "risk-engine", "is_halted": engine.is_halted}


@app.get("/risk/status")
async def get_risk_status():
    """Retourne l'état complet du Risk Engine."""
    return engine.get_status()


@app.post("/risk/check")
async def check_trade(req: TradeCheckRequest):
    """Valide si un trade est autorisé selon les limites de risque."""
    allowed, message = engine.check_trade_safety(req.symbol, req.side, req.amount, req.current_pnl)
    return {"allowed": allowed, "message": message}


@app.post("/risk/reset")
async def reset_daily_risk():
    """Reset manuel des compteurs journaliers."""
    engine.reset_daily()
    return {"status": "reset", "message": "Daily risk counters reset."}


@app.post("/risk/update-capital")
async def update_capital(new_capital: float):
    """Met a jour le capital de reference."""
    engine.capital = new_capital
    return {"status": "updated", "new_capital": new_capital}
