import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
from contextlib import asynccontextmanager

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
PRIMARY_MODEL = "deepseek-r1:latest"
try:
    import mock_data
except ImportError:
    from . import mock_data

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AI Service starting...")
    yield
    print("👋 AI Service shutting down.")

app = FastAPI(title="AI Service (100% Local Ollama)", lifespan=lifespan)

# CORS — allow dashboard and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    symbol: str
    market_context: Dict[str, Any]
    news_context: Dict[str, Any]

class GenericAnalysisRequest(BaseModel):
    context: str
    instruction: str


async def get_available_models() -> List[str]:
    """Recupere la liste de tous les modeles telecharges dans Ollama."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            tags_url = OLLAMA_URL.replace("/api/generate", "/api/tags")
            response = await client.get(tags_url)
            if response.status_code == 200:
                return [m['name'] for m in response.json().get('models', [])]
    except Exception as e:
        print(f"Erreur connexion Ollama: {e}")
    return []


async def check_model_availability(model_name: str) -> bool:
    """Verifie si un modele specifique est disponible dans Ollama."""
    available = await get_available_models()
    return any(model_name in m for m in available)


@app.post("/ai/summary")
async def get_ai_summary(req: AnalysisRequest):
    """
    Genere un resume AI base sur les donnees de marche et news.
    """
    if USE_MOCK_DATA:
        return {
            "status": "success", 
            "model_used": "mock-decider-v1", 
            "ai_decision": mock_data.get_mock_ai_decision(req.symbol)
        }

    available_models = await get_available_models()

    if not available_models:
        raise HTTPException(
            status_code=503,
            detail="Aucun modele trouve dans Ollama. Lancez 'docker exec -it ollama ollama pull deepseek-r1:latest'"
        )

    # Logique de Fallback dynamique
    model_to_use = PRIMARY_MODEL if PRIMARY_MODEL in available_models else available_models[0]

    if model_to_use != PRIMARY_MODEL:
        print(f"⚠️ {PRIMARY_MODEL} non disponible. Utilisation du fallback: {model_to_use}")

    prompt = f"""
    En tant que Trader Quantitatif Senior, analyse cette situation pour {req.symbol}:
    
    [DONNEES DE MARCHE]
    Price Change: {req.market_context.get('change_24h', 'N/A')}%
    Volume: {req.market_context.get('volume_24h', 'N/A')}
    
    [ACTUALITE ET SENTIMENT]
    Sentiment Global: {req.news_context.get('sentiment', 'N/A')} (Score: {req.news_context.get('score', 'N/A')})
    
    Fournis un resume tres bref, une recommendation (Acheter/Vendre/Attendre) et un ajustement de risque (1-10).
    Reponds uniquement en format JSON: {{"summary": "...", "recommendation": "...", "risk_level": ...}}
    """

    payload = {
        "model": model_to_use,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            if response.status_code == 200:
                return {"status": "success", "model_used": model_to_use, "ai_decision": response.json().get("response", {})}
            else:
                raise HTTPException(status_code=response.status_code, detail="Erreur interne Ollama")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama timeout — le modele met trop de temps a repondre.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de connexion Ollama: {str(e)}")


@app.post("/ai/analyze")
async def analyze_generic(req: GenericAnalysisRequest):
    """
    Genere une analyse AI generique basee sur un contexte et une instruction.
    """
    if USE_MOCK_DATA:
        return {
            "status": "success", 
            "model_used": "mock-analyzer-v1", 
            "response": f"MOCK ANALYSIS: Based on {len(req.context)} chars of context, the recommendation is to CONTINUE scaling."
        }

    available_models = await get_available_models()
    if not available_models:
        raise HTTPException(status_code=503, detail="Ollama models unavailable")

    model_to_use = PRIMARY_MODEL if PRIMARY_MODEL in available_models else available_models[0]

    prompt = f"""
    CONTEXT:
    {req.context}
    
    INSTRUCTION:
    {req.instruction}
    
    Reponds comme un Expert Trader Quantitatif. Sois precis et direct.
    """

    payload = {
        "model": model_to_use,
        "prompt": prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            if response.status_code == 200:
                return {"status": "success", "model_used": model_to_use, "response": response.json().get("response", "")}
            else:
                raise HTTPException(status_code=response.status_code, detail="Ollama error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check — verifie la connexion Ollama et la disponibilite du modele."""
    if USE_MOCK_DATA:
        return {
            "status": "ok",
            "mode": "mock",
            "service": "ai-service"
        }
    try:
        is_ready = await check_model_availability(PRIMARY_MODEL)
        models = await get_available_models()
        return {
            "status": "ok" if is_ready else "waiting_for_model",
            "primary_model": PRIMARY_MODEL,
            "model_ready": is_ready,
            "available_models": models,
            "service": "ai-service"
        }
    except Exception as e:
        return {"status": "error", "detail": str(e), "service": "ai-service"}
