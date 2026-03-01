"use client";

import TradingChart from "@/components/charts/TradingChart";
import { useDashboardStore } from "@/store/dashboardStore";
import LayoutControl from "@/components/layout/LayoutControl";

export default function Home() {
  const { gridLayout } = useDashboardStore();

  if (gridLayout === '1x1') {
    return (
      <div className="w-full h-full bg-[#131722] p-1 relative">
         <TradingChart symbol="BTC/USDT" containerId="chart_main" />
      </div>
    );
  }

  return (
    <div className="w-full h-full grid grid-cols-2 grid-rows-2 gap-2 bg-[#131722] p-1 relative">
      <div className="border border-[#2a2e39] rounded overflow-hidden shadow-xl">
        <TradingChart symbol="BTC/USDT" containerId="chart_1" />
      </div>
      <div className="border border-[#2a2e39] rounded overflow-hidden shadow-xl">
        <TradingChart symbol="ETH/USDT" containerId="chart_2" />
      </div>
      <div className="border border-[#2a2e39] rounded overflow-hidden shadow-xl">
        <TradingChart symbol="SOL/USDT" containerId="chart_3" />
      </div>
      <div className="border border-[#2a2e39] rounded overflow-hidden shadow-xl">
        <TradingChart symbol="BNB/USDT" containerId="chart_4" />
      </div>
    </div>
  );
}
