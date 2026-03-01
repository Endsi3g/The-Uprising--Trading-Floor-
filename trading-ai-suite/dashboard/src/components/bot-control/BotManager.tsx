"use client";

import { cn } from "@/utils/cn";
import { useState } from "react";

const BOTS = [
  { id: "hb", name: "Hummingbot", strategy: "Pure Market Making", status: "Running", uptime: "2d 4h" },
  { id: "ft", name: "Freqtrade", strategy: "SampleStrategy", status: "Stopped", uptime: "0s" },
  { id: "ob", name: "OctoBot", strategy: "Neural Network v2", status: "Running", uptime: "14h 22m" },
];

export default function BotManager() {
  const [activeBots, setActiveBots] = useState(BOTS);

  return (
    <div className="p-4 bg-[#1e222d] border border-[#2a2e39] rounded-lg shadow-2xl glass m-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#d1d4dc] uppercase tracking-wider flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#089981]"></span> Multi-Engine Control
        </h3>
        <button className="text-[10px] bg-[#2a2e39] hover:bg-[#363c4e] px-2 py-1 rounded text-[#787b86] transition-colors">DEPLOY NEW</button>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {activeBots.map((bot) => (
          <div key={bot.id} className="p-3 bg-[#131722]/50 border border-[#2a2e39] rounded flex items-center justify-between group hover:border-[#2962ff]/50 transition-all">
            <div className="flex flex-col">
               <div className="flex items-center gap-2">
                 <span className="text-xs font-bold">{bot.name}</span>
                 <span className={cn(
                   "text-[9px] px-1 rounded uppercase font-black",
                   bot.status === "Running" ? "bg-[#089981]/20 text-[#089981]" : "bg-[#f23645]/20 text-[#f23645]"
                 )}>{bot.status}</span>
               </div>
               <span className="text-[10px] text-[#787b86] italic">{bot.strategy}</span>
            </div>
            
            <div className="flex items-center gap-4">
               <div className="text-right flex flex-col justify-center">
                 <span className="text-[10px] text-[#787b86]">UPTIME</span>
                 <span className="text-[10px] font-mono">{bot.uptime}</span>
               </div>
               <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="p-1.5 hover:bg-[#2a2e39] rounded text-[#089981]">▶</button>
                  <button className="p-1.5 hover:bg-[#2a2e39] rounded text-[#f23645]">■</button>
                  <button className="p-1.5 hover:bg-[#2a2e39] rounded text-[#787b86]">⚙</button>
               </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
