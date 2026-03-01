# Changelog

All notable changes to the **Trading AI Suite** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.2.0] — 2026-03-01

### Added
- **Risk Engine API**: Full FastAPI wrapper exposing `/risk/status`, `/risk/check`, `/risk/reset`, `/risk/update-capital`
- **CORS Middleware**: All 4 backend services now allow cross-origin requests from the dashboard
- **Health Endpoints**: `/health` on all services (broker-hub, news-hub, ai-service, risk-engine)
- **Bulk Ticker Endpoint**: `/tickers` on broker-hub for fetching multiple symbols at once
- **CoinDesk Scraping**: News-hub now scrapes CoinDesk as secondary source for redundancy
- **Enhanced Sentiment**: Expanded keyword dictionary from 18 → 60+ weighted words with granular labels (Very Bullish/Very Bearish)
- **Requirements Files**: Pinned dependencies for all 4 Python services (`requirements-broker.txt`, etc.)
- **Docker Healthchecks**: All services in `docker-compose.yml` now have healthcheck directives
- **Docker Networking**: Explicit `trading-net` bridge network for inter-service communication
- **Service Dependencies**: `ai-service` depends on `ollama` health before starting
- **`.gitignore`**: Comprehensive ignore rules for the project
- **GitHub Actions CI**: Lint, build, and test automation on push/PR
- **GitHub Actions Release**: Auto-generate GitHub releases from changelog on tag push
- **Dashboard API Service**: Centralized type-safe API client (`api.ts`) for all backends
- **BotManager in Layout**: Component is now actually rendered in the dashboard layout

### Fixed
- **`ai_service.py`**: `check_model_availability()` was undefined — caused health endpoint crash
- **`ai_sentinel.py`**: `__main__` called non-existent `analyze_market()` — now calls `unified_analysis()`
- **Deprecated APIs**: Replaced `@app.on_event("startup/shutdown")` with modern `lifespan` context manager in all services
- **Docker Compose**: Removed deprecated `version: "3.9"` key — not needed in modern Docker
- **Ollama URL Parsing**: Fixed `/api/generate` → `/api/tags` URL construction for model listing

### Changed
- **AI Service**: Added model name to response body for transparency
- **Sentiment Engine**: Switched from binary (-0.8/0/0.8) to continuous weighted scoring (-1.0 to 1.0)
- **Risk Engine**: Added trade history tracking (last 10 trades stored in memory)
- **Docker Services**: Now install deps from `requirements.txt` files instead of inline `pip install`
- **Test System**: Added risk-engine service check, `--mock` flag, and JSON report output

---

## [0.1.0] — 2026-02-28

### Added
- **BrokerHub**: Unified CCXT layer via FastAPI (Binance, KuCoin, Bybit) — `/balances`, `/ticker`, `/order`, `/orders`
- **NewsHub**: CoinTelegraph scraper with basic sentiment analysis — `/news`, `/sentiment`
- **AI Service**: Ollama wrapper with DeepSeek-R1 primary + dynamic fallback — `/ai/summary`
- **AI Sentinel**: Standalone AI decision module with dual-model fallback
- **Risk Engine**: Circuit breakers, cooldowns, daily loss limits, consecutive loss protection
- **Hummingbot**: Market making bot integration via Docker
- **Freqtrade**: Algo trading engine with EMA crossover strategy (`SampleStrategy`)
- **OctoBot**: Neural network trading engine integration
- **Dashboard**: Next.js 16 + TailwindCSS 4 + Lightweight Charts — TradingView++ clone
  - Multi-layout charting (2×2 grid)
  - Watchlist with price/change display
  - AI Insights panel with news + sentiment
  - Bot Manager with start/stop controls
  - Status bar with service health indicators
- **Docker Compose**: Full orchestration of 7 services
- **Test System**: Automated endpoint validation script (`test_system.py`)
- **Week 1 Guide**: Setup documentation (`week1_setup_guide.md`)
