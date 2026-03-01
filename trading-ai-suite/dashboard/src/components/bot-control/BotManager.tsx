"use client";

import { cn } from "@/utils/cn";
import { useEffect, useState, useCallback } from "react";
import { fetchBotsStatus, controlBot, BotStatus } from "@/services/api";

export default function BotManager() {
  const [bots, setBots] = useState<BotStatus[]>([]);
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);

  const loadBots = useCallback(async () => {
    const res = await fetchBotsStatus();
    if (res?.status === "ok") {
      setBots(res.bots);
      setError(null);
    } else {
      setError("Failed to fetch bot status");
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      await loadBots();
    };
    init();
    const interval = setInterval(loadBots, 10000);
    return () => clearInterval(interval);
  }, [loadBots]);

  const handleAction = async (botId: string, action: string) => {
    setLoading((prev) => ({ ...prev, [botId]: true }));
    const res = await controlBot(botId, action);
    if (res?.status === "success") {
      await loadBots();
    } else {
      setError(`Failed to ${action} ${botId}`);
    }
    setLoading((prev) => ({ ...prev, [botId]: false }));
  };

  return (
    <div className="p-4 bg-[#1e222d] border border-[#2a2e39] rounded-lg shadow-2xl glass m-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#d1d4dc] uppercase tracking-wider flex items-center gap-2">
          <span className={cn("w-2 h-2 rounded-full", bots.length > 0 ? "bg-[#089981]" : "bg-[#f23645]")}></span> 
          Multi-Engine Control
        </h3>
        {error && <span className="text-[10px] text-[#f23645] font-bold uppercase">{error}</span>}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {bots.length > 0 ? bots.map((bot) => (
          <div key={bot.id} className="p-3 bg-[#131722]/50 border border-[#2a2e39] rounded flex items-center justify-between group hover:border-[#2962ff]/50 transition-all">
            <div className="flex flex-col">
               <div className="flex items-center gap-2">
                 <span className="text-xs font-bold">{bot.name}</span>
                 <span className={cn(
                   "text-[9px] px-1 rounded uppercase font-black",
                   bot.status === "Running" ? "bg-[#089981]/20 text-[#089981]" : "bg-[#f23645]/20 text-[#f23645]"
                 )}>{bot.status}</span>
               </div>
               <span className="text-[10px] text-[#787b86] italic">Uptime: {bot.uptime}</span>
            </div>
            
            <div className="flex items-center gap-2">
               {loading[bot.id] ? (
                 <span className="text-[10px] text-[#787b86] animate-pulse">Processing...</span>
               ) : (
                 <div className="flex gap-1">
                    <button 
                      onClick={() => handleAction(bot.id, 'start')}
                      disabled={bot.status === 'Running'}
                      className="p-1.5 hover:bg-[#089981]/10 rounded text-[#089981] disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Start"
                    >▶</button>
                    <button 
                      onClick={() => handleAction(bot.id, 'stop')}
                      disabled={bot.status !== 'Running'}
                      className="p-1.5 hover:bg-[#f23645]/10 rounded text-[#f23645] disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Stop"
                    >■</button>
                    <button 
                      onClick={() => handleAction(bot.id, 'restart')}
                      className="p-1.5 hover:bg-[#787b86]/10 rounded text-[#787b86]"
                      title="Restart"
                    >🔄</button>
                 </div>
               )}
            </div>
          </div>
        )) : (
          <div className="col-span-3 py-4 text-center text-[#787b86] text-xs">
            {error ? "No bots connected. Ensure Docker is running." : "Searching for engines..."}
          </div>
        )}
      </div>
    </div>
  );
}
