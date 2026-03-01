"use client";

import { useEffect, useRef } from 'react';
import { createChart, ColorType, IChartApi, ISeriesApi, CandlestickData } from 'lightweight-charts';
import { cn } from '@/utils/cn';

interface TradingChartProps {
  symbol?: string;
  containerId?: string;
  data?: CandlestickData[];
  className?: string;
}

export default function TradingChart({ symbol = "BTC/USDT", data = [], className }: TradingChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

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
    
    // @ts-expect-error - addCandlestickSeries exists on chart instance but type definition may be incomplete
    seriesRef.current = chart.addCandlestickSeries({
      upColor: '#089981',
      downColor: '#f23645',
      borderVisible: false,
      wickUpColor: '#089981',
      wickDownColor: '#f23645',
    });

    if (data && data.length > 0 && seriesRef.current) {
      seriesRef.current.setData(data);
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
          <span className="text-[#d1d4dc] font-semibold uppercase tracking-wider">{symbol}</span>
          <span>O <span className="text-[#089981]">--</span></span>
          <span>H <span className="text-[#089981]">--</span></span>
          <span>L <span className="text-[#f23645]">--</span></span>
          <span>C <span className="text-[#d1d4dc]">--</span></span>
      </div>
    </div>
  );
}


