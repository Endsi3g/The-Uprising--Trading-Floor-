import os
import httpx
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
from contextlib import asynccontextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIService")

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
PRIMARY_MODEL = "deepseek-r1:1.5b"

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AI Service starting in PRODUCTION mode...")
    yield
    logger.info("👋 AI Service shutting down.")

app = FastAPI(title="AI Service (Production - Local Ollama)", lifespan=lifespan)

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
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                return [m['name'] for m in response.json().get('models', [])]
    except Exception as e:
        logger.error(f"Ollama connection check failed: {e}")
    return []

@app.post("/ai/summary")
async def get_market_summary(req: AnalysisRequest):
    """Genere un resume decisionnel base sur le marche et les news."""
    
    available_models = await get_available_models()
    if not available_models:
        raise HTTPException(status_code=503, detail="Ollama disconnected or no models found.")

    model_to_use = PRIMARY_MODEL if any(PRIMARY_MODEL in m for m in available_models) else available_models[0]

    context = f"Symbol: {req.symbol}\n\nMarket Data: {req.market_context}\n\nNews Data: {req.news_context}"

    prompt = f"""
    En tant qu'expert en trading crypto, analyse les donnees suivantes et donne une recommandation claire.
    Sois concis, factuel et evalue le niveau de risque (1-5).
    
    DONNEES:
    {context}
    
    RETOURNE UN JSON:
    {{
        "summary": "...",
        "recommendation": "ACHETER / VENDRE / ATTENDRE",
        "risk_level": 3
    }}
    """

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model_to_use,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )

            if response.status_code == 200:
                return {
                    "status": "success",
                    "model_used": model_to_use,
                    "ai_decision": response.json().get("response", "{}")
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Ollama inference error")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI processing timed out.")
    except Exception as e:
        logger.error(f"AI Service Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/analyze")
async def analyze_generic(req: GenericAnalysisRequest):
    """Genere une analyse AI generique basee sur un contexte et une instruction."""
    
    available_models = await get_available_models()
    if not available_models:
        raise HTTPException(status_code=503, detail="Ollama unavailable")

    model_to_use = PRIMARY_MODEL if any(PRIMARY_MODEL in m for m in available_models) else available_models[0]

    prompt = f"CONTEXT:\n{req.context}\n\nINSTRUCTION:\n{req.instruction}\n\nReponds comme un Trader Pro."

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model_to_use,
                    "prompt": prompt,
                    "stream": False
                }
            )
            if response.status_code == 200:
                return {
                    "status": "success",
                    "model_used": model_to_use,
                    "response": response.json().get("response", "")
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Ollama error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check — verifie Ollama."""
    try:
        models = await get_available_models()
        if not models:
            raise HTTPException(status_code=503, detail={
                "status": "error",
                "service": "ai-service",
                "available_models": [],
                "mode": "production"
            })
        return {
            "status": "ok",
            "service": "ai-service",
            "available_models": models,
            "mode": "production"
        }
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=503, detail={
            "status": "error", 
            "service": "ai-service", 
            "error": str(e),
            "mode": "production"
        })
