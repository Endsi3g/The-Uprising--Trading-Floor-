import httpx
import asyncio
import os

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
PRIMARY_MODEL = "deepseek-r1:latest"
FALLBACK_MODEL = "llama3.2:latest"


async def check_model_availability(model_name: str) -> bool:
    """Verifie si un modele est disponible dans Ollama."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            tags_url = OLLAMA_URL.replace("/api/generate", "/api/tags")
            response = await client.get(tags_url)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                return any(model_name in m for m in models)
    except Exception:
        return False
    return False


async def get_ai_decision(prompt: str, context: str = "") -> str:
    """Genere une decision AI avec fallback automatique."""

    # Check if primary model is available
    model_to_use = PRIMARY_MODEL
    is_primary_available = await check_model_availability(PRIMARY_MODEL)

    if not is_primary_available:
        print(f"⚠️ {PRIMARY_MODEL} non trouve sur Ollama. Tentative d'utilisation du fallback: {FALLBACK_MODEL}")
        model_to_use = FALLBACK_MODEL
        if not await check_model_availability(FALLBACK_MODEL):
            return "ERROR: Aucun modele AI (DeepSeek ou Llama) n'est pret. Lancez 'ollama pull deepseek-r1:latest' d'abord."

    payload = {
        "model": model_to_use,
        "prompt": f"Context: {context}\n\nTask: {prompt}\n\nFormat: Reponds en JSON avec 'action' (BUY/SELL/HOLD), 'reason' et 'risk_score' (0-1).",
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            if response.status_code == 200:
                return response.json().get("response", "No response content.")
            else:
                return f"ERROR: Ollama Error {response.status_code}"
    except Exception as e:
        return f"ERROR: Connection to Ollama failed. Verifiez 'docker ps'. ({e})"


async def unified_analysis(symbol: str, market_data: dict, news_sentiment: dict):
    """Analyse combinee Broker + News via DeepSeek-R1."""
    prompt = f"""
    Donnees Marche ({symbol}): Change 24h: {market_data.get('change_24h')}%, RSI: {market_data.get('rsi')}
    Sentiment Actualite: {news_sentiment.get('sentiment')}, Score: {news_sentiment.get('score')}
    Nombre de News: {news_sentiment.get('news_count')}
    
    Analyse si la tendance est saine pour une entree agressive.
    """
    decision = await get_ai_decision(prompt, context="Senior Quantitative Trading AI")
    print(f"--- ANALYSE DEEPSEEK ({symbol}) ---\n{decision}")
    return decision


if __name__ == "__main__":
    # Test standalone — unified_analysis demo
    asyncio.run(unified_analysis(
        "BTC",
        {"change_24h": 5.2, "rsi": 62},
        {"sentiment": "Bullish", "score": 0.8, "news_count": 5}
    ))
