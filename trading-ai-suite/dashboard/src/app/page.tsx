import TradingChart from "@/components/charts/TradingChart";
import Watchlist from "@/components/watchlist/Watchlist";
import AIPanel from "@/components/ai/AIPanel";

export default function Home() {
  return (
    <div className="w-full h-full grid grid-cols-2 grid-rows-2 gap-px bg-[#2a2e39]">
      <TradingChart className="bg-[#131722]" />
      <TradingChart className="bg-[#131722]" />
      <TradingChart className="bg-[#131722]" />
      <TradingChart className="bg-[#131722]" />
    </div>
  );
}
// Note: Integration happens in layout.tsx. I am just verifying home page content here.
