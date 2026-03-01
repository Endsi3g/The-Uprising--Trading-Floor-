import random
from datetime import datetime, timedelta

def get_mock_balances():
    """Synthetic account balances for various exchanges."""
    return {
        "binance": {"BTC": 1.25, "ETH": 15.6, "USDT": 12500.50, "SOL": 450.0},
        "kucoin": {"BTC": 0.05, "KCS": 1000.0, "USDT": 2100.0},
        "bybit": {"BTC": 0.35, "USDT": 5000.0}
    }

def get_mock_tickers(symbols=None):
    """Synthetic price data with realistic 24h changes."""
    if not symbols:
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "ARB/USDT"]
    
    base_prices = {
        "BTC/USDT": 65000.0,
        "ETH/USDT": 3500.0,
        "SOL/USDT": 145.0,
        "ARB/USDT": 1.85
    }
    
    results = {}
    for s in symbols:
        price = base_prices.get(s, 100.0) * (1 + (random.random() - 0.5) * 0.02)
        results[s] = {
            "last": round(price, 2),
            "percentage": round((random.random() - 0.4) * 5, 2),
            "quoteVolume": round(random.random() * 100000000, 2),
            "high": round(price * 1.05, 2),
            "low": round(price * 0.95, 2),
        }
    return results

def get_mock_news(symbol="BTC"):
    """Synthetic news headlines with sentiment analysis."""
    headlines = [
        f"{symbol} breakthrough: Institutional adoption triples in Q1",
        f"Critical update: {symbol} network maintains 100% uptime during surge",
        f"Market Analysis: Why {symbol} is the top pick for hedge funds this week",
        f"Regulatory Win: New framework favors {symbol} growth in EU markets",
        f"Tech Insight: {symbol} protocol efficiency reaches all-time high",
        f"Community Spotlight: The Uprising users report 15% gains using {symbol} bots"
    ]
    
    news = []
    for i, title in enumerate(headlines):
        news.append({
            "title": title,
            "source": random.choice(["The Uprising News", "QuantDaily", "CryptoPulse"]),
            "url": "https://theuprising.trading/news/mock",
            "published_at": (datetime.now() - timedelta(hours=i*4)).isoformat(),
            "sentiment": round(0.5 + (random.random() * 0.5), 2)  # Predominantly bullish mock data
        })
    return news

def get_mock_ai_decision(symbol):
    """Synthetic AI signals and risk assessments."""
    return {
        "summary": f"Strong accumulation detected for {symbol}. Market sentiment is highly bullish following institutional entries. Volatility remains within optimal ranges for arbitrage.",
        "recommendation": "Acheter (BUY)",
        "risk_level": random.randint(2, 4)
    }
