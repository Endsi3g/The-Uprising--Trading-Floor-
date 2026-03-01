"use client";

import { cn } from "@/utils/cn";
import { useEffect, useState } from "react";
import { fetchNews, fetchSentiment, fetchAIHealth, NewsItem, SentimentData, HealthStatus } from "@/services/api";

export default function AIPanel() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [aiHealth, setAiHealth] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      const [newsData, sentimentData, healthData] = await Promise.all([
        fetchNews("BTC", 5),
        fetchSentiment("BTC"),
        fetchAIHealth(),
      ]) as [NewsItem[] | null, SentimentData | null, HealthStatus | null];

      if (newsData && newsData.length > 0 && !newsData[0]?.title?.includes("Aucune news")) {
        setNews(newsData);
      }
      if (sentimentData) setSentiment(sentimentData);
      if (healthData) setAiHealth(healthData);
      setIsLoading(false);
    }

    loadData();
    const interval = setInterval(loadData, 60000); // Refresh every 60s
    return () => clearInterval(interval);
  }, []);

  const recommendationColor = sentiment
    ? sentiment.sentiment.includes("Bullish") ? "text-[#089981]"
    : sentiment.sentiment.includes("Bearish") ? "text-[#f23645]"
    : "text-[#787b86]"
    : "text-[#787b86]";

  return (
    <div className="flex flex-col h-full bg-[#1e222d] border-t border-[#2a2e39]">
      <div className="p-4 border-b border-[#2a2e39] text-xs font-bold text-[#787b86] flex items-center justify-between">
        <span>AI INSIGHTS & NEWS</span>
        {aiHealth && (
          <span className={cn(
            "text-[9px] px-1.5 py-0.5 rounded font-bold uppercase",
            aiHealth.status === "ok" ? "bg-[#089981]/20 text-[#089981]" : "bg-[#f23645]/20 text-[#f23645]"
          )}>
            {aiHealth.status === "ok" ? "CONNECTED" : "OFFLINE"}
          </span>
        )}
      </div>

      <div className="p-4 bg-[#2962ff]/5 border-b border-[#2a2e39]">
        <div className="text-[10px] text-[#2962ff] font-bold uppercase tracking-widest mb-1">AI Sentinel Overview</div>
        {sentiment ? (
          <>
            <div className="text-sm font-semibold mb-2">
              Sentiment: <span className={recommendationColor}>{sentiment.sentiment.toUpperCase()}</span>
              <span className="text-[10px] text-[#787b86] ml-2">(Score: {sentiment.score})</span>
            </div>
            <p className="text-[11px] text-[#787b86] leading-relaxed">
              Based on {sentiment.news_count} articles from {sentiment.sources?.join(", ") || "multiple sources"}.
            </p>
          </>
        ) : (
          <div className="text-sm text-[#787b86]">
            {isLoading ? "Loading AI analysis..." : "AI service unavailable — using mock data."}
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto no-scrollbar">
        {news.length > 0 ? news.map((item, i) => (
          <a
            key={i}
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 border-b border-[#2a2e39]/50 hover:bg-[#2a2e39]/30 transition-colors"
          >
            <div className="flex justify-between items-start mb-1">
              <span className="text-[10px] text-[#787b86] tracking-tighter uppercase">{item.source}</span>
              <span className={cn(
                "text-[10px] px-1.5 py-0.5 rounded font-bold uppercase",
                item.sentiment > 0.2 ? "bg-[#089981]/20 text-[#089981]"
                : item.sentiment < -0.2 ? "bg-[#f23645]/20 text-[#f23645]"
                : "bg-white/10 text-white/50"
              )}>
                {item.sentiment > 0.2 ? "Bullish" : item.sentiment < -0.2 ? "Bearish" : "Neutral"}
              </span>
            </div>
            <h4 className="text-xs font-medium text-[#d1d4dc] leading-snug">{item.title}</h4>
          </a>
        )) : (
          // Fallback mock news
          [
            { title: "Bitcoin hits new local high as ETF inflows surge", source: "Mock", sentiment: 0.8 },
            { title: "Fed meeting minutes hint at potential rate pause", source: "Mock", sentiment: 0 },
            { title: "Exchange outflows reaching record levels", source: "Mock", sentiment: 0.7 },
          ].map((mock, i) => (
            <div key={i} className="p-4 border-b border-[#2a2e39]/50 hover:bg-[#2a2e39]/30 transition-colors opacity-60">
              <div className="flex justify-between items-start mb-1">
                <span className="text-[10px] text-[#787b86] tracking-tighter uppercase">{mock.source}</span>
                <span className={cn(
                  "text-[10px] px-1.5 py-0.5 rounded font-bold uppercase",
                  mock.sentiment > 0 ? "bg-[#089981]/20 text-[#089981]" : "bg-white/10 text-white/50"
                )}>
                  {mock.sentiment > 0 ? "Bullish" : "Neutral"}
                </span>
              </div>
              <h4 className="text-xs font-medium text-[#d1d4dc] leading-snug">{mock.title}</h4>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
