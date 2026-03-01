"use client";

import { create } from 'zustand';

interface DashboardState {
  chartLayout: '1x1' | '2x2';
  setChartLayout: (layout: '1x1' | '2x2') => void;
  botStatus: Record<string, string>;
  updateBotStatus: (id: string, status: string) => void;
  activeSymbol: string;
  setActiveSymbol: (symbol: string) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  chartLayout: '2x2',
  setChartLayout: (layout) => set({ chartLayout: layout }),
  botStatus: {
    hb: "Running",
    ft: "Stopped",
    ob: "Running"
  },
  updateBotStatus: (id, status) => set((state) => ({
    botStatus: { ...state.botStatus, [id]: status }
  })),
  activeSymbol: 'BTC/USDT',
  setActiveSymbol: (symbol) => set({ activeSymbol: symbol }),
}));
