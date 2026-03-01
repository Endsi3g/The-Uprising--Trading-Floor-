"use client";

import { useEffect, useRef } from 'react';
import { createChart, ColorType, ISeriesApi, CandlestickData } from 'lightweight-charts';
import { cn } from '@/utils/cn';

interface TradingChartProps {
  data?: CandlestickData[];
  className?: string;
}

export default function TradingChart({ data = [], className }: TradingChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chartOptions = {
      layout: {
        background: { type: ColorType.Solid, color: '#131722' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
        horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
      },
      crosshair: {
        mode: 0,
      },
      rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 0.1)',
      },
      timeScale: {
        borderColor: 'rgba(197, 203, 206, 0.1)',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    };

    const chart = createChart(chartContainerRef.current, {
        ...chartOptions,
        width: chartContainerRef.current.clientWidth,
        height: chartContainerRef.current.clientHeight,
    });
    
    chartRef.current = chart;

    const candlestickSeries = (chart as any).addCandlestickSeries({
      upColor: '#089981',
      downColor: '#f23645',
      borderVisible: false,
      wickUpColor: '#089981',
      wickDownColor: '#f23645',
    });

    if (data.length > 0) {
      candlestickSeries.setData(data);
    } else {
        // Mock data if none provided
        const mockData = generateMockData();
        candlestickSeries.setData(mockData);
    }

    const handleResize = () => {
      chart.applyOptions({ 
        width: chartContainerRef.current?.clientWidth,
        height: chartContainerRef.current?.clientHeight 
      });
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data]);

  return (
    <div className={cn("w-full h-full relative group", className)}>
      <div ref={chartContainerRef} className="w-full h-full" />
      <div className="absolute top-4 left-4 z-10 bg-black/40 backdrop-blur-md px-3 py-1 rounded-md border border-white/5 text-xs flex gap-3 text-[#787b86]">
          <span className="text-[#d1d4dc] font-semibold uppercase tracking-wider">BTC/USDT</span>
          <span>O <span className="text-[#089981]">91,245.50</span></span>
          <span>H <span className="text-[#089981]">92,100.00</span></span>
          <span>L <span className="text-[#f23645]">90,800.00</span></span>
          <span>C <span className="text-[#d1d4dc]">91,450.20</span></span>
      </div>
    </div>
  );
}

function generateMockData(): CandlestickData[] {
  const data: CandlestickData[] = [];
  const baseTime = new Date('2024-01-01T00:00:00Z').getTime() / 1000;
  let lastClose = 90000;

  for (let i = 0; i < 100; i++) {
    const open = lastClose;
    const high = open + Math.random() * 500;
    const low = open - Math.random() * 500;
    const close = low + Math.random() * (high - low);
    
    data.push({
      time: (baseTime + i * 86400) as any,
      open,
      high,
      low,
      close,
    });
    lastClose = close;
  }
  return data;
}
