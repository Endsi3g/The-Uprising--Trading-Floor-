"use client";

import { useDashboardStore } from "@/store/dashboardStore";
import { cn } from "@/utils/cn";
import { useState, useEffect } from "react";
import { fetchAIHealth } from "@/services/api";

export default function Navbar() {
  const { gridLayout, setGridLayout } = useDashboardStore();
  const [isHealthOk, setIsHealthOk] = useState(true);

  useEffect(() => {
    const check = async () => {
      const health = await fetchAIHealth();
      setIsHealthOk(health?.status === "ok");
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="col-span-3 border-b border-[#2a2e39] bg-[#1e222d]/80 backdrop-blur-md flex items-center justify-between px-4 z-20 sticky top-0 h-12">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 group cursor-pointer" onClick={() => window.location.reload()}>
          <div className="w-8 h-8 rounded bg-gradient-to-tr from-[#2962ff] to-[#00d2ff] flex items-center justify-center font-black text-white glow shadow-2xl transition-transform group-hover:scale-105 active:scale-95 text-xs">U</div>
          <h1 className="text-xs font-black tracking-tighter uppercase group-hover:text-[#2962ff] transition-colors">The Uprising <span className="text-[#787b86] font-normal">Trading Floor</span></h1>
        </div>
        
        <nav className="flex items-center gap-4 border-l border-[#2a2e39] pl-6 h-6">
          <div className="text-[11px] font-bold text-white uppercase tracking-wider relative group cursor-pointer px-1">
            Dashboard
            <div className="absolute -bottom-[15px] left-0 right-0 h-[2px] bg-[#2962ff] glow"></div>
          </div>
          <div className="text-[11px] font-bold text-[#787b86] hover:text-white uppercase tracking-wider transition-colors cursor-pointer">Strategies</div>
          <div className="text-[11px] font-bold text-[#787b86] hover:text-white uppercase tracking-wider transition-colors cursor-pointer">Backtest</div>
        </nav>
      </div>

      <div className="flex items-center gap-4">
        {/* Layout Control Integrated in Navbar for 12-Year-Old Simplicity */}
        <div className="flex items-center bg-[#131722] rounded p-0.5 border border-[#2a2e39] mr-2">
           <button 
             onClick={() => setGridLayout("1x1")}
             className={cn("px-2 py-1 text-[10px] rounded transition-all font-bold", gridLayout === "1x1" ? "bg-[#2962ff] text-white shadow-lg" : "text-[#787b86] hover:text-white")}
           >1x1</button>
           <button 
             onClick={() => setGridLayout("2x2")}
             className={cn("px-2 py-1 text-[10px] rounded transition-all font-bold", gridLayout === "2x2" ? "bg-[#2962ff] text-white shadow-lg" : "text-[#787b86] hover:text-white")}
           >2x2</button>
        </div>

        <div className={cn(
          "hidden lg:flex items-center gap-2 px-3 py-1 bg-opacity-10 border rounded-full transition-all",
          isHealthOk ? "bg-[#089981]/10 border-[#089981]/20 glow-green" : "bg-[#f23645]/10 border-[#f23645]/20"
        )}>
          <span className={cn("w-1.5 h-1.5 rounded-full animate-pulse", isHealthOk ? "bg-[#089981] shadow-[0_0_5px_#089981]" : "bg-[#f23645]")}></span>
          <span className={cn("text-[9px] font-black uppercase tracking-widest", isHealthOk ? "text-[#089981]" : "text-[#f23645]")}>
            {isHealthOk ? "AI Pulse Active" : "AI Offline"}
          </span>
        </div>
        
        <button 
          onClick={() => alert("Deployment Sequence Initialized...")}
          className="bg-[#2962ff] hover:bg-[#1e4bd8] text-white text-[10px] font-black px-4 py-1.5 rounded shadow-lg glow transition-all active:scale-95 uppercase tracking-wider border border-white/5"
        >
          One-Click Deploy
        </button>
        
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#2a2e39] to-[#131722] border border-[#363c4e] flex items-center justify-center text-[10px] font-black text-[#d1d4dc] cursor-pointer hover:border-[#2962ff] hover:text-white transition-all shadow-xl">JD</div>
      </div>
    </header>
  );
}
