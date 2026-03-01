"use client";

import { cn } from "@/utils/cn";
import { useEffect, useState } from "react";
import { fetchTickers, TickerData } from "@/services/api";

interface WatchlistItem {
  symbol: string;
  price: string;
  change: string;
  color: string;
}

const FALLBACK_WATCHLIST: WatchlistItem[] = [
  { symbol: "BTC/USDT", price: "—", change: "—", color: "text-[#787b86]" },
  { symbol: "ETH/USDT", price: "—", change: "—", color: "text-[#787b86]" },
  { symbol: "SOL/USDT", price: "—", change: "—", color: "text-[#787b86]" },
  { symbol: "BNB/USDT", price: "—", change: "—", color: "text-[#787b86]" },
];

function formatPrice(price: number | null): string {
  if (price === null || price === undefined) return "—";
  return price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatChange(change: number | null): { text: string; color: string } {
  if (change === null || change === undefined) return { text: "—", color: "text-[#787b86]" };
  const sign = change >= 0 ? "+" : "";
  return {
    text: `${sign}${change.toFixed(2)}%`,
    color: change >= 0 ? "text-[#089981]" : "text-[#f23645]",
  };
}

export default function Watchlist() {
  const [items, setItems] = useState<WatchlistItem[]>(FALLBACK_WATCHLIST);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    async function loadTickers() {
      const data = await fetchTickers("binance");
      if (data) {
        const newItems: WatchlistItem[] = Object.entries(data).map(([symbol, ticker]) => {
          const { text, color } = formatChange(ticker.change);
          return {
            symbol,
            price: formatPrice(ticker.last),
            change: text,
            color,
          };
        });
        if (newItems.length > 0) {
          setItems(newItems);
          setIsLive(true);
        }
      }
    }

    loadTickers();
    interval = setInterval(loadTickers, 15000); // Refresh every 15s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-full bg-[#1e222d]">
      <div className="p-4 border-b border-[#2a2e39] text-xs font-bold text-[#787b86] flex justify-between">
        <span>SYMBOL</span>
        <div className="flex gap-8">
          <span>LAST</span>
          <span>CHG%</span>
        </div>
      </div>
      {isLive && (
        <div className="px-4 py-1 bg-[#089981]/10 text-[9px] text-[#089981] font-bold uppercase tracking-widest">
          🟢 Live Data
        </div>
      )}
      <div className="flex-1 overflow-y-auto no-scrollbar">
        {items.map((item) => (
          <div
            key={item.symbol}
            className="px-4 py-3 border-b border-[#2a2e39]/50 flex items-center justify-between cursor-pointer hover:bg-[#2a2e39] transition-colors group"
          >
            <div className="flex flex-col">
              <span className="text-sm font-semibold group-hover:text-[#2962ff] transition-colors">{item.symbol}</span>
              <span className="text-[10px] text-[#787b86] uppercase">Binance</span>
            </div>
            <div className="flex gap-6 items-center text-sm font-mono">
              <span>{item.price}</span>
              <span className={cn("min-w-[50px] text-right", item.color)}>{item.change}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
