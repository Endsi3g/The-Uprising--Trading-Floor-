# Changelog

All notable changes to the **Trading AI Suite** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.1.0] — 2026-03-02

### Added

- **Ultimate Unified Entry**: Added `bin/setup-and-start.ps1`, a single command to Install, Configure, Resolve Conflicts, and Launch the entire Trading Floor.
- **Port Recovery (Windows)**: Hardened automated port 11434 recovery to target both `ollama.exe` and the `ollama app.exe` tray application (to prevent auto-respawn).
- **Robust Docker Healthchecks**: Replaced fragile `curl`-based healthchecks with native Python `urllib` and built-in `ollama list` checks to support standard slim container images.
- **Unified Startup (Windows)**: Added `bin/start-suite.ps1` to automate the entire flow: environment setup, Docker backends, and dashboard execution in one command.
- **Standalone Start (Windows)**: `start.ps1` now automatically detects the Conda environment and runs without manual activation.
- **Automated Build**: `install.ps1` now handles Cython compilation (`build_ext`) and package linking (`conda develop`) automatically.
- **DLL Runtime Reliability**: Switched to `conda run` execution to ensure system library paths are correctly loaded on Windows.

### Success

- **NATIVE WINDOWS HUB**: Verified success starting Hummingbot via CLI and fully integrated `trading-ai-suite` from a clean Windows install.
- **ZERO-CONFIG RUN**: All components now start natively without requiring manual path configurations or environment variables.

### Fixed

- **Windows Import Error**: Moved Unix-only module imports (`grp`, `pwd`) behind conditional checks for native support.
- **Path Detection**: Improved robustness of environment path extraction to handle non-standard directory layouts.
- **Documentation**: Corrected repository directory targets in `README.md` installation guides.
- **News Hub**: Fixed undefined `news` variable crash in sentiment analysis service.
- **E2E Testing**: Added null-response protection to browser UI tests.

---

## [1.0.0] — 2026-03-01

### Added

- **Desktop Application**: Electron wrapper for native Windows (.exe) and macOS (.dmg) installers.
- **Build Orchestrator**: `build-desktop.py` script for one-command multi-platform packaging.
- **E2E Dashboard Test**: `test_dashboard_e2e.py` verifies all backend services are in production mode.
- **Production `.env.example`**: Complete template with all required API keys and service URLs.

### Changed

- **PRODUCTION MODE ENFORCED**: All services (`broker_hub`, `news_hub`, `ai_service`) now reject mock data.
- **Mock Data Removed**: `USE_MOCK_DATA` flag and `mock_data` imports fully eliminated from all services.
- **AI Service Rewrite**: Consolidated endpoints, proper error propagation, and Ollama health verification.
- **BrokerHub Hardening**: Returns HTTP 503 when no exchanges are configured instead of an empty response.
- **NewsHub Hardening**: Returns empty list instead of placeholder text when scraping fails.

### Removed

- Mock data fallback paths from `broker_hub.py`, `news_hub.py`, and `ai_service.py`.

---

## [0.4.0] — 2026-03-01

### Added (v0.4.0)

- **Electron Desktop App**: Native desktop wrapper with `electron-serve`, dark title bar, and 1440×900 default window.
- **Multi-Platform Builds**: `electron-builder` config producing `.exe` (NSIS), `.dmg`, and `.AppImage` installers.
- **Playwright E2E Tests**: `test_dashboard_e2e.py` with 10 tests covering page load, layout, charts, watchlist, AI panel, bot manager, and status bar.
- **Dashboard npm Scripts**: `electron-dev` and `electron-build` for one-command desktop packaging.

### Changed (v0.4.0)

- **`.env.example`**: Now documents all 15 environment variables across all services (Alert Hub, Risk Engine, Dashboard API URLs).
- **`next.config.ts`**: Switched to static export mode (`output: "export"`) for Electron compatibility.
- **`package.json`**: Added project metadata (`author`, `description`), Electron entry point, and full builder config.

---

## [0.3.0] — 2026-03-01

### Added (v0.3.0)

- **Alert Hub Refinement**: Robust background broadcasting to Discord/Telegram via FastAPI `BackgroundTasks`.
- **Reporting Automation**: `performance_recap.py` script for AI-generated weekly PnL reports.
- **AI Service Expansion**: New `/ai/analyze` endpoint for generic quantitative market analysis.
- **Master Test Suite**: Comprehensive E2E system check (`master_test_suite.py`) validating the full flow.
- **Release Automation**: `release_manager.py` for one-click versioning and GitHub release creation.

### Changed (v0.3.0)

- **Risk Engine Alerts**: Now sends proactive warnings on single trade stop-losses and critical alerts on consecutive losses.
- **Improved Logging**: Added structured logging and timestamp formats across all suite services.

### Fixed (v0.3.0)

- **Connectivity Paths**: Standardized service discovery URLs using internal Docker networking.

---

## [0.2.0] — 2026-03-01

### Added (v0.2.0)

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

### Fixed (v0.2.0)

- **`ai_service.py`**: `check_model_availability()` was undefined — caused health endpoint crash
- **`ai_sentinel.py`**: `__main__` called non-existent `analyze_market()` — now calls `unified_analysis()`
- **Deprecated APIs**: Replaced `@app.on_event("startup/shutdown")` with modern `lifespan` context manager in all services
- **Docker Compose**: Removed deprecated `version: "3.9"` key — not needed in modern Docker
- **Ollama URL Parsing**: Fixed `/api/generate` → `/api/tags` URL construction for model listing

### Changed (v0.2.0)

- **AI Service**: Added model name to response body for transparency
- **Sentiment Engine**: Switched from binary (-0.8/0/0.8) to continuous weighted scoring (-1.0 to 1.0)
- **Risk Engine**: Added trade history tracking (last 10 trades stored in memory)
- **Docker Services**: Now install deps from `requirements.txt` files instead of inline `pip install`
- **Test System**: Added risk-engine service check, `--mock` flag, and JSON report output

---

## [0.1.0] — 2026-02-28

### Added (v0.1.0)
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
