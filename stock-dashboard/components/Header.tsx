"use client";
import { useEffect, useState } from "react";

export default function Header({ date }: { date: string }) {
  const [time, setTime] = useState("");

  useEffect(() => {
    const tick = () =>
      setTime(new Date().toLocaleTimeString("ko-KR", { hour12: false }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header
      style={{ background: "linear-gradient(180deg,#0d1424 0%,#0a0e1a 100%)", borderBottom: "1px solid #1e3a5f" }}
      className="sticky top-0 z-50 px-6 py-4"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* 로고 */}
        <div className="flex items-center gap-3">
          <div
            style={{ background: "linear-gradient(135deg,#f59e0b,#fbbf24)" }}
            className="w-9 h-9 rounded-lg flex items-center justify-center text-black font-black text-lg"
          >
            S
          </div>
          <div>
            <p className="text-white font-bold text-base leading-tight">StockSignal</p>
            <p style={{ color: "#64748b" }} className="text-xs">증권 리포트 대시보드</p>
          </div>
        </div>

        {/* 중앙 배지 */}
        <div
          style={{ border: "1px solid rgba(245,158,11,0.3)", background: "rgba(245,158,11,0.08)" }}
          className="hidden md:flex items-center gap-2 px-4 py-1.5 rounded-full"
        >
          <span className="pulse-dot w-2 h-2 rounded-full bg-green-400 inline-block" />
          <span style={{ color: "#a3b1c6" }} className="text-sm">LIVE</span>
          <span style={{ color: "#f59e0b" }} className="text-sm font-medium ml-1">
            한경컨센서스 기준
          </span>
        </div>

        {/* 날짜·시간 */}
        <div className="text-right">
          <p style={{ color: "#f59e0b" }} className="text-sm font-semibold">{date}</p>
          <p style={{ color: "#64748b" }} className="text-xs font-mono">{time}</p>
        </div>
      </div>
    </header>
  );
}
