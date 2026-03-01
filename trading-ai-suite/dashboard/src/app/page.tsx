"use client";

import TradingChart from "@/components/charts/TradingChart";
import { useDashboardStore } from "@/store/dashboardStore";
import LayoutControl from "@/components/layout/LayoutControl";

export default function Home() {
  const chartLayout = useDashboardStore((state) => state.chartLayout);

  if (chartLayout === '1x1') {
    return (
      <div className="w-full h-full bg-[#131722] p-1 relative">
         <LayoutControl />
         <TradingChart className="bg-[#131722] border border-[#2a2e39] rounded" />
      </div>
    );
  }

  return (
    <div className="w-full h-full grid grid-cols-2 grid-rows-2 gap-1 bg-[#2a2e39] p-1 relative">
      <LayoutControl />
      <TradingChart className="bg-[#131722] rounded" />
      <TradingChart className="bg-[#131722] rounded" />
      <TradingChart className="bg-[#131722] rounded" />
      <TradingChart className="bg-[#131722] rounded" />
    </div>
  );
}
