# Week 1: Foundation Setup & Paper Trading Protocol

## 🔒 1. API Key Security & Hardening

Before connecting any exchange, you MUST follow these security rules:

### Exchange Configuration
- **Binance / Kucoin / Bybit**:
  - **Permissions**: Enable `Read` and `Spot Trading` ONLY. 
  - **Withdrawals**: MUST be **DISABLED**.
  - **IP Whitelisting**: Recommend whitelisting your VPS IP (or home IP if running locally) for all API keys.
  - **Passphrase**: For Kucoin, use a complex passphrase (16+ chars).

### Local Storage
- Never commit `.env` or `conf/conf_client.yml` to GitHub.
- Use the provided `.env.example` as a template for your local `.env`.

---

## 🧪 2. 48h Paper Trading Protocol

Before deploying $500 live, we must validate the system's baseline.

### Step 1: Initialize Hummingbot
1. Start the containers: `docker compose up -d`.
2. Enter the instance: `docker attach hummingbot`.
3. Set your master password (from `.env`).

### Step 2: Configure Paper Trading
1. In Hummingbot, run: `config paper_trade_enabled: True`.
2. Connect your mock exchanges: `connect binance` (use dummy keys if needed, or real ones with paper trade active).
3. Select a strategy: `create` -> `pure_market_making`.
4. Target Pairs: `BTC-USDT`, `ETH-USDT`, `SOL-USDT`.

### Step 3: Optimization Parameters (Balanced Mode)
- **Bid Spread**: 0.5%
- **Ask Spread**: 0.5%
- **Order Amount**: $50 (mock)
- **Inventory Skew**: Enabled (to maintain 50/50 balance)

---

## ✅ 3. Week 1 Validation Checklist

| Criteria | Target | Verification Method |
|----------|--------|---------------------|
| **Connectivity** | 100% Uptime | Check `logs/` for reconnection errors. |
| **Execution** | > 10 trades/day | Verify in `hummingbot` terminal via `history`. |
| **Spread Capture** | Consistent | Review PnL after 48h. |
| **AI Base** | Responsive | Run `ollama list` and verify `llama3.2` is loaded. |

---

## 🚀 4. Next Steps
Once the 48h trial is successful, we will proceed to **Week 2: AI Sentinel Integration**, where we link Ollama to the trade decision logic.
