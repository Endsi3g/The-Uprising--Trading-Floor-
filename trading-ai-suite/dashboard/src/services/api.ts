// Centralized API client for all Trading AI Suite backend services
// Provides type-safe fetch wrappers for all endpoints

const API_CONFIG = {
  brokerHub: process.env.NEXT_PUBLIC_BROKER_HUB_URL || 'http://localhost:8001',
  newsHub: process.env.NEXT_PUBLIC_NEWS_HUB_URL || 'http://localhost:8002',
  aiService: process.env.NEXT_PUBLIC_AI_SERVICE_URL || 'http://localhost:8003',
  riskEngine: process.env.NEXT_PUBLIC_RISK_ENGINE_URL || 'http://localhost:8004',
};

// --- Types ---
export interface TickerData {
  last: number | null;
  change: number | null;
  volume: number | null;
  high: number | null;
  low: number | null;
}

export interface NewsItem {
  title: string;
  source: string;
  url: string;
  published_at: string;
  sentiment: number;
}

export interface SentimentData {
  symbol: string;
  sentiment: string;
  score: number;
  news_count: number;
  sources: string[];
}

export interface RiskStatus {
  capital: number;
  daily_start_capital: number;
  current_loss: number;
  is_halted: boolean;
  cooldown_until: string | null;
  consecutive_losses: number;
  max_daily_loss_pct: number;
  max_trade_loss_pct: number;
  circuit_breaker_pct: number;
  cooldown_hours: number;
  recent_trades: Array<{
    symbol: string;
    side: string;
    amount: number;
    pnl: number;
    timestamp: string;
  }>;
}

export interface HealthStatus {
  status: string;
  service: string;
  [key: string]: unknown;
}

export interface AIDecision {
  status: string;
  model_used: string;
  ai_decision: unknown;
}

// --- Generic fetch ---
async function apiFetch<T>(url: string, options?: RequestInit): Promise<T | null> {
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

// --- Broker Hub ---
export async function fetchTickers(exchange: string, symbols: string = 'BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT'): Promise<Record<string, TickerData> | null> {
  return apiFetch(`${API_CONFIG.brokerHub}/tickers?exchange=${exchange}&symbols=${encodeURIComponent(symbols)}`);
}

export async function fetchBalances(): Promise<Record<string, Record<string, number>> | null> {
  return apiFetch(`${API_CONFIG.brokerHub}/balances`);
}

export async function fetchBrokerHealth(): Promise<HealthStatus | null> {
  return apiFetch(`${API_CONFIG.brokerHub}/health`);
}

export interface BotStatus {
  id: string;
  name: string;
  status: string;
  uptime: string;
}

export interface BotsResponse {
  status: string;
  bots: BotStatus[];
}

export interface ControlResponse {
  status: string;
  message: string;
}

export async function fetchBotsStatus(): Promise<BotsResponse | null> {
  return apiFetch(`${API_CONFIG.brokerHub}/bots`);
}

export async function controlBot(botId: string, action: string): Promise<ControlResponse | null> {
  return apiFetch(`${API_CONFIG.brokerHub}/bots/${botId}/${action}`, {
    method: 'POST',
  });
}

// --- News Hub ---
export async function fetchNews(symbol: string = 'BTC', limit: number = 10): Promise<NewsItem[] | null> {
  return apiFetch(`${API_CONFIG.newsHub}/news?symbol=${symbol}&limit=${limit}`);
}

export async function fetchSentiment(symbol: string = 'BTC'): Promise<SentimentData | null> {
  return apiFetch(`${API_CONFIG.newsHub}/sentiment?symbol=${symbol}`);
}

export async function fetchNewsHealth(): Promise<HealthStatus | null> {
  return apiFetch(`${API_CONFIG.newsHub}/health`);
}

// --- AI Service ---
export async function fetchAISummary(symbol: string, marketContext: Record<string, unknown>, newsContext: Record<string, unknown>): Promise<AIDecision | null> {
  return apiFetch(`${API_CONFIG.aiService}/ai/summary`, {
    method: 'POST',
    body: JSON.stringify({
      symbol,
      market_context: marketContext,
      news_context: newsContext,
    }),
  });
}

export async function fetchAIHealth(): Promise<HealthStatus | null> {
  return apiFetch(`${API_CONFIG.aiService}/health`);
}

// --- Risk Engine ---
export async function fetchRiskStatus(): Promise<RiskStatus | null> {
  return apiFetch(`${API_CONFIG.riskEngine}/risk/status`);
}

export async function checkTradeRisk(symbol: string, side: string, amount: number, currentPnl: number): Promise<{ allowed: boolean; message: string } | null> {
  return apiFetch(`${API_CONFIG.riskEngine}/risk/check`, {
    method: 'POST',
    body: JSON.stringify({
      symbol,
      side,
      amount,
      current_pnl: currentPnl,
    }),
  });
}

export async function fetchRiskHealth(): Promise<HealthStatus | null> {
  return apiFetch(`${API_CONFIG.riskEngine}/health`);
}

// --- Aggregated Health ---
export async function fetchAllHealth(): Promise<Record<string, HealthStatus | null>> {
  const [broker, news, ai, risk] = await Promise.all([
    fetchBrokerHealth(),
    fetchNewsHealth(),
    fetchAIHealth(),
    fetchRiskHealth(),
  ]);

  return { broker, news, ai, risk };
}
