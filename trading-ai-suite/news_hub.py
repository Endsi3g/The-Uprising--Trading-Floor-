import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from contextlib import asynccontextmanager
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("📰 NewsHub starting...")
    yield
    print("👋 NewsHub shutting down.")


app = FastAPI(title="NewsHub API (100% Free Scraper)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Enhanced Sentiment Dictionary (60+ words with weighted scores) ---
BULLISH_WORDS = {
    # Strong bullish (weight 2)
    "surge": 2, "soar": 2, "moon": 2, "skyrocket": 2, "breakout": 2, "parabolic": 2, "pump": 2,
    # Medium bullish (weight 1)
    "bull": 1, "rally": 1, "buy": 1, "gain": 1, "up": 1, "high": 1, "bullish": 1,
    "recover": 1, "rebound": 1, "adoption": 1, "approval": 1, "accumulate": 1,
    "inflow": 1, "growth": 1, "optimism": 1, "upgrade": 1, "outperform": 1,
    "boom": 1, "milestone": 1, "record": 1, "mainstream": 1, "institutional": 1,
}

BEARISH_WORDS = {
    # Strong bearish (weight 2)
    "crash": 2, "collapse": 2, "plunge": 2, "hack": 2, "scam": 2, "fraud": 2, "ban": 2,
    # Medium bearish (weight 1)
    "bear": 1, "dump": 1, "sell": 1, "down": 1, "low": 1, "loss": 1, "bearish": 1,
    "decline": 1, "drop": 1, "fear": 1, "panic": 1, "outflow": 1, "regulation": 1,
    "investigation": 1, "lawsuit": 1, "warning": 1, "risk": 1, "bubble": 1,
    "liquidation": 1, "insolvency": 1, "bankruptcy": 1, "exploit": 1,
}


@app.get("/health")
async def health_check():
    """Health check for NewsHub."""
    return {"status": "ok", "service": "news-hub", "sources": ["cointelegraph", "coindesk"]}


@app.get("/news")
async def get_crypto_news(symbol: str = "BTC", limit: int = 10) -> List[Dict]:
    """Scrape les news depuis CoinTelegraph et CoinDesk sans API payante."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    news_list = []

    # --- Source 1: CoinTelegraph ---
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            url = f"https://cointelegraph.com/tags/{symbol.lower()}"
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                url = "https://cointelegraph.com/category/latest-news"
                response = await client.get(url, headers=headers)

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all("article", class_="post-card-inline", limit=limit)

            for article in articles:
                title_tag = article.find("span", class_="post-card-inline__title")
                link_tag = article.find("a", class_="post-card-inline__title-link")
                date_tag = article.find("time")

                if title_tag and link_tag:
                    title = title_tag.text.strip()
                    if symbol.upper() in title.upper() or "latest-news" not in url:
                        news_list.append({
                            "title": title,
                            "source": "CoinTelegraph",
                            "url": "https://cointelegraph.com" + link_tag["href"],
                            "published_at": date_tag["datetime"] if date_tag else "Unknown",
                            "sentiment": calculate_weighted_sentiment(title)
                        })
    except Exception as e:
        print(f"⚠️ CoinTelegraph scraping failed: {e}")

    # --- Source 2: CoinDesk (fallback) ---
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            url = f"https://www.coindesk.com/tag/{symbol.lower()}/"
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all("a", {"data-testid": "content-label"}, limit=limit // 2)

                for article in articles:
                    title = article.text.strip()
                    if title and len(title) > 10:
                        news_list.append({
                            "title": title,
                            "source": "CoinDesk",
                            "url": "https://www.coindesk.com" + article.get("href", ""),
                            "published_at": "Recent",
                            "sentiment": calculate_weighted_sentiment(title)
                        })
    except Exception as e:
        print(f"⚠️ CoinDesk scraping failed: {e}")

    if not news_list:
        return []

    return news_list[:limit]


def calculate_weighted_sentiment(text: str) -> float:
    """Calcul de sentiment pondéré avec dictionnaire étendu (60+ mots)."""
    text_lower = text.lower()
    bull_score = 0
    bear_score = 0

    for word, weight in BULLISH_WORDS.items():
        if word in text_lower:
            bull_score += weight

    for word, weight in BEARISH_WORDS.items():
        if word in text_lower:
            bear_score += weight

    total = bull_score + bear_score
    if total == 0:
        return 0.0

    # Normalize to -1.0 (very bearish) to 1.0 (very bullish)
    raw_score = (bull_score - bear_score) / max(total, 1)

    # Clamp between -1 and 1
    return max(-1.0, min(1.0, raw_score))


@app.get("/sentiment")
async def get_sentiment_summary(symbol: str) -> Dict:
    """Combine les news pour donner un score de sentiment global."""
    if not news:
        return {"symbol": symbol, "sentiment": "Neutral", "score": 0.5, "news_count": 0, "sources": []}

    avg_sentiment = sum(item.get("sentiment", 0) for item in news) / len(news)

    # Mapping score (-1 a 1) vers echelle (0 a 1) pour l'AI
    normalized_score = (avg_sentiment + 1) / 2

    sentiment_label = "Neutral"
    if normalized_score > 0.6:
        sentiment_label = "Bullish"
    if normalized_score > 0.8:
        sentiment_label = "Very Bullish"
    if normalized_score < 0.4:
        sentiment_label = "Bearish"
    if normalized_score < 0.2:
        sentiment_label = "Very Bearish"

    sources = list(set(item.get("source", "Unknown") for item in news))

    return {
        "symbol": symbol,
        "sentiment": sentiment_label,
        "score": round(normalized_score, 3),
        "news_count": len(news),
        "sources": sources
    }
