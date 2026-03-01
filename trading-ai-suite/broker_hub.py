import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import ccxt.async_support as ccxt

exchanges = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize exchange connections on startup, close on shutdown."""
    # --- Startup ---
    if os.getenv("BINANCE_API_KEY"):
        exchanges["binance"] = ccxt.binance({
            "apiKey": os.getenv("BINANCE_API_KEY"),
            "secret": os.getenv("BINANCE_API_SECRET"),
            "enableRateLimit": True,
        })

    if os.getenv("KUCOIN_API_KEY"):
        exchanges["kucoin"] = ccxt.kucoin({
            "apiKey": os.getenv("KUCOIN_API_KEY"),
            "secret": os.getenv("KUCOIN_API_SECRET"),
            "password": os.getenv("KUCOIN_PASSPHRASE"),
            "enableRateLimit": True,
        })

    if os.getenv("BYBIT_API_KEY"):
        exchanges["bybit"] = ccxt.bybit({
            "apiKey": os.getenv("BYBIT_API_KEY"),
            "secret": os.getenv("BYBIT_API_SECRET"),
            "enableRateLimit": True,
        })

    print(f"🔗 BrokerHub: {len(exchanges)} exchanges configurés — {list(exchanges.keys())}")
    yield

    # --- Shutdown ---
    for exchange in exchanges.values():
        await exchange.close()
    print("👋 BrokerHub: Toutes les connexions fermées.")


app = FastAPI(title="BrokerHub API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check — retourne les exchanges connectes."""
    return {
        "status": "ok",
        "service": "broker-hub",
        "exchanges_connected": list(exchanges.keys()),
        "exchange_count": len(exchanges)
    }


@app.get("/balances")
async def get_aggregated_balances():
    """Recupere les balances de tous les exchanges connectes."""
    if not exchanges:
        return {"warning": "Aucun exchange configure. Verifiez votre fichier .env"}

    tasks = []
    exchange_names = list(exchanges.keys())

    for name in exchange_names:
        tasks.append(exchanges[name].fetch_balance())

    results = await asyncio.gather(*tasks, return_exceptions=True)

    aggregated = {}
    for name, res in zip(exchange_names, results):
        if isinstance(res, Exception):
            aggregated[name] = {"error": str(res)}
        else:
            clean_balance = {k: v for k, v in res.get('total', {}).items() if v > 0}
            aggregated[name] = clean_balance

    return aggregated


@app.get("/ticker")
async def get_ticker(symbol: str, exchange: str):
    """Recupere le ticker d'un symbole sur un exchange."""
    if exchange not in exchanges:
        raise HTTPException(status_code=400, detail=f"Exchange {exchange} non configure")

    try:
        ticker = await exchanges[exchange].fetch_ticker(symbol)
        return ticker
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tickers")
async def get_multiple_tickers(exchange: str, symbols: str = "BTC/USDT,ETH/USDT,SOL/USDT"):
    """Recupere les tickers de plusieurs symboles d'un coup."""
    if exchange not in exchanges:
        raise HTTPException(status_code=400, detail=f"Exchange {exchange} non configure")

    symbol_list = [s.strip() for s in symbols.split(",")]
    results = {}
    for symbol in symbol_list:
        try:
            ticker = await exchanges[exchange].fetch_ticker(symbol)
            results[symbol] = {
                "last": ticker.get("last"),
                "change": ticker.get("percentage"),
                "volume": ticker.get("quoteVolume"),
                "high": ticker.get("high"),
                "low": ticker.get("low"),
            }
        except Exception as e:
            results[symbol] = {"error": str(e)}

    return results


class OrderRequest(BaseModel):
    exchange: str
    symbol: str
    type: str  # 'market' ou 'limit'
    side: str  # 'buy' ou 'sell'
    amount: float
    price: float = None


@app.post("/order")
async def place_order(order: OrderRequest):
    """Place un ordre sur l'exchange specifie."""
    if order.exchange not in exchanges:
        raise HTTPException(status_code=400, detail=f"Exchange {order.exchange} non configure")

    ex = exchanges[order.exchange]
    try:
        if order.type == 'limit':
            if not order.price:
                raise HTTPException(status_code=400, detail="Price requis pour limit order")
            res = await ex.create_limit_order(order.symbol, order.side, order.amount, order.price)
        else:
            res = await ex.create_market_order(order.symbol, order.side, order.amount)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders")
async def get_orders(symbol: str, exchange: str):
    """Liste les ordres ouverts pour un symbole sur un exchange."""
    if exchange not in exchanges:
        raise HTTPException(status_code=400, detail=f"Exchange {exchange} non configure")
    try:
        orders = await exchanges[exchange].fetch_open_orders(symbol)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
