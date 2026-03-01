"use client";

import { useDashboardStore } from "@/store/dashboardStore";
import { cn } from "@/utils/cn";

export default function LayoutControl() {
  const { chartLayout, setChartLayout } = useDashboardStore();

  return (
    <div className="absolute top-4 right-4 z-10 bg-[#1e222d] border border-[#2a2e39] rounded-md flex p-1 shadow-lg">
      <button 
        onClick={() => setChartLayout('1x1')}
        className={cn(
          "w-8 h-8 rounded flex items-center justify-center transition-colors",
          chartLayout === '1x1' ? "bg-[#2962ff]/20 text-[#2962ff]" : "text-[#787b86] hover:text-[#d1d4dc] hover:bg-[#2a2e39]"
        )}
        title="Single Focus"
      >
        <div className="w-4 h-4 border-2 border-current rounded-sm"></div>
      </button>
      
      <button 
        onClick={() => setChartLayout('2x2')}
        className={cn(
          "w-8 h-8 rounded flex items-center justify-center transition-colors ml-1",
          chartLayout === '2x2' ? "bg-[#2962ff]/20 text-[#2962ff]" : "text-[#787b86] hover:text-[#d1d4dc] hover:bg-[#2a2e39]"
        )}
        title="Grid View (4 Assets)"
      >
        <div className="w-4 h-4 grid grid-cols-2 grid-rows-2 gap-[2px]">
           <div className="bg-current rounded-sm"></div>
           <div className="bg-current rounded-sm"></div>
           <div className="bg-current rounded-sm"></div>
           <div className="bg-current rounded-sm"></div>
        </div>
      </button>
    </div>
  );
}
