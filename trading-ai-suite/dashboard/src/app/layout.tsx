import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/utils/cn";
import Watchlist from "@/components/watchlist/Watchlist";
import AIPanel from "@/components/ai/AIPanel";
import BotManager from "@/components/bot-control/BotManager";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Trading AI Suite | TradingView++",
  description: "Advanced Automated Trading Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={cn(inter.className, "bg-[#131722] text-[#d1d4dc] selection:bg-[#2962ff]/30 h-screen w-screen overflow-hidden")}>
        <div className="tv-grid">
          {/* Top Navbar */}
          <header className="col-span-3 border-b border-[#2a2e39] bg-[#1e222d] flex items-center px-4 z-20">
            <div className="font-bold text-lg text-[#2962ff] mr-8 tracking-tighter">AI SUITE</div>
            <div className="flex gap-4 text-[11px] font-bold text-[#787b86] uppercase tracking-wider">
              {/* Note: The store will be imported in a client wrapper later, but we will make these links static in layout for now and put toggles inside page.tsx or a separate component */}
              <span className="cursor-pointer hover:text-white transition-colors border-b-2 border-[#2962ff] pb-3 pt-3">Dashboard</span>
              <span className="cursor-pointer hover:text-white transition-colors pb-3 pt-3">Strategy Finder</span>
            </div>
            
            <div className="ml-auto flex items-center gap-4">
               <span className="text-[10px] text-[#787b86] font-bold tracking-widest mr-2 border-r border-[#2a2e39] pr-4">
                  PRO MODE
               </span>
               <button className="bg-[#2962ff] hover:bg-[#2962ff]/80 text-white text-[10px] font-bold px-3 py-1 rounded transition-colors uppercase tracking-widest shadow-[0_0_10px_rgba(41,98,255,0.3)]">Deploy All</button>
            </div>
          </header>

          {/* Left Icon Sidebar */}
          <aside className="border-r border-[#2a2e39] bg-[#1e222d] flex flex-col items-center py-4 gap-6 z-20">
             <div className="p-2 text-[#2962ff] cursor-pointer transition-colors border-l-2 border-[#2962ff] bg-[#2962ff]/5" title="Chart Grid">
               📊
             </div>
             <div className="p-2 text-[#787b86] cursor-pointer hover:text-[#2962ff] transition-colors" title="AI Agents">
               🤖
             </div>
             <div className="p-2 text-[#787b86] cursor-pointer hover:text-[#2962ff] transition-colors" title="Settings">
               ⚙️
             </div>
          </aside>

          {/* Main Content (Charts + Bot Control) */}
          <main className="bg-[#131722] relative overflow-hidden flex flex-col">
            <div className="flex-1 overflow-hidden relative">
              {children}
            </div>
            <div className="h-auto max-h-[200px] overflow-y-auto border-t border-[#2a2e39]">
              <BotManager />
            </div>
          </main>

          {/* Right Data Sidebar (Watchlist & AI) */}
          <aside className="border-l border-[#2a2e39] bg-[#1e222d] flex flex-col z-20 overflow-hidden">
             <div className="flex-1 overflow-hidden flex flex-col min-h-0">
                <div className="flex-1 overflow-hidden">
                  <Watchlist />
                </div>
                <div className="h-[300px] border-t border-[#2a2e39]">
                  <AIPanel />
                </div>
             </div>
          </aside>

          {/* Bottom Status Bar */}
          <footer className="col-span-3 border-t border-[#2a2e39] bg-[#1e222d] flex items-center px-4 text-[9px] text-[#787b86] uppercase font-bold tracking-widest z-20">
             <div className="flex items-center gap-6 w-full">
               <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#089981] animate-pulse"></span> BROKER: ONLINE</span>
               <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#089981]"></span> AI SENTINEL: ANALYZING</span>
               <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#787b86]"></span> DOCKED: BYBIT</span>
               <span className="ml-auto flex gap-4">
                 <span>MARKET: <span className="text-white">OPEN</span></span>
                 <span>SESSIONS: <span className="text-[#2962ff]">3 ACTIVE</span></span>
                 <span>PNL (24H): <span className="text-[#089981]">+$1,245.00 (+2.45%)</span></span>
               </span>
             </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
