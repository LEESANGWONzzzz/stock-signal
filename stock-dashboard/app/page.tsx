import { promises as fs } from "fs";
import path from "path";
import Header from "@/components/Header";
import StatCards from "@/components/StatCards";
import UpsideChart from "@/components/UpsideChart";
import StockTable from "@/components/StockTable";

interface Stock {
  날짜: string;
  종목명: string;
  종목코드: string;
  목표주가: number;
  리포트수: number;
  투자의견: string;
  증권사: string;
  현재가: number;
  "상승여력(%)": number;
}

async function getStocks(): Promise<Stock[]> {
  const filePath = path.join(process.cwd(), "public", "stocks.json");
  const raw = await fs.readFile(filePath, "utf-8");
  const data: Stock[] = JSON.parse(raw);
  return data
    .filter((s) => s.현재가 > 0 && s.목표주가 > 0)
    .sort((a, b) => b["상승여력(%)"] - a["상승여력(%)"])
    .slice(0, 10);
}

export default async function Home() {
  const stocks = await getStocks();
  const date = stocks[0]?.날짜 ?? new Date().toISOString().slice(0, 10);

  return (
    <div style={{ background: "#0a0e1a" }} className="min-h-screen">
      <Header date={date} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">

        {/* 페이지 타이틀 */}
        <div className="mb-8 fade-in">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full"
              style={{ background: "rgba(245,158,11,0.15)", color: "#f59e0b", border: "1px solid rgba(245,158,11,0.3)" }}>
              TODAY
            </span>
            <span style={{ color: "#64748b" }} className="text-xs">{date} 기준</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white leading-tight">
            목표주가 상승여력{" "}
            <span className="gradient-text">TOP 10</span>
          </h1>
          <p style={{ color: "#64748b" }} className="mt-2 text-sm">
            한경컨센서스 기업 리포트 기반 · 상승여력 = (목표주가 − 현재가) ÷ 현재가 × 100
          </p>
        </div>

        {/* 통계 카드 */}
        <StatCards stocks={stocks} />

        {/* 1위 하이라이트 배너 */}
        {stocks[0] && (
          <div
            className="rounded-2xl p-6 mb-8 fade-in"
            style={{
              background: "linear-gradient(135deg,#1a1200,#2d1f00)",
              border: "1px solid rgba(245,158,11,0.4)",
              boxShadow: "0 0 40px rgba(245,158,11,0.08)",
            }}
          >
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">🏆</span>
                  <span style={{ color: "#f59e0b" }} className="text-sm font-semibold uppercase tracking-wider">
                    상승여력 1위
                  </span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-black text-white">
                  {stocks[0].종목명}
                </h2>
                <p style={{ color: "#78716c" }} className="text-sm mt-1">
                  {stocks[0].종목코드} · {stocks[0].증권사}
                </p>
              </div>
              <div className="flex gap-8 sm:gap-12 text-center">
                <div>
                  <p style={{ color: "#64748b" }} className="text-xs mb-1">현재가</p>
                  <p className="text-xl font-bold text-white font-mono">
                    {stocks[0].현재가.toLocaleString()}
                    <span style={{ color: "#64748b" }} className="text-sm ml-1">원</span>
                  </p>
                </div>
                <div>
                  <p style={{ color: "#64748b" }} className="text-xs mb-1">목표주가</p>
                  <p className="text-xl font-bold font-mono" style={{ color: "#fbbf24" }}>
                    {stocks[0].목표주가.toLocaleString()}
                    <span style={{ color: "#78716c" }} className="text-sm ml-1">원</span>
                  </p>
                </div>
                <div>
                  <p style={{ color: "#64748b" }} className="text-xs mb-1">상승여력</p>
                  <p className="text-3xl font-black" style={{ color: "#10b981" }}>
                    +{stocks[0]["상승여력(%)"].toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 차트 */}
        <UpsideChart stocks={stocks} />

        {/* 테이블 */}
        <StockTable stocks={stocks} />

      </main>

      {/* 푸터 */}
      <footer
        className="mt-16 px-6 py-8 text-center text-xs"
        style={{ borderTop: "1px solid #1e3a5f", color: "#334155" }}
      >
        <p className="font-semibold mb-1" style={{ color: "#475569" }}>StockSignal Dashboard</p>
        <p>데이터 출처: 한경컨센서스 (consensus.hankyung.com) · 현재가: FinanceDataReader</p>
        <p className="mt-1">본 사이트는 투자 참고 자료를 제공하며, 투자 판단의 책임은 본인에게 있습니다.</p>
      </footer>
    </div>
  );
}
