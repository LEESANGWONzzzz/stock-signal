"use client";

interface Stock {
  종목명: string;
  종목코드: string;
  현재가: number;
  목표주가: number;
  "상승여력(%)": number;
  투자의견: string;
  증권사: string;
}

interface Props {
  stocks: Stock[];
}

export default function StatCards({ stocks }: Props) {
  const top1 = stocks[0];
  const buyCount = stocks.filter(
    (s) => s.투자의견 === "Buy" || s.투자의견 === "매수"
  ).length;
  const avgUpside =
    stocks.reduce((a, b) => a + b["상승여력(%)"], 0) / stocks.length;
  const maxUpside = Math.max(...stocks.map((s) => s["상승여력(%)"]));

  const cards = [
    {
      label: "분석 종목 수",
      value: `${stocks.length}종목`,
      sub: "오늘자 기업 리포트",
      icon: "📋",
      color: "#3b82f6",
    },
    {
      label: "Buy / 매수 비중",
      value: `${buyCount}/${stocks.length}`,
      sub: `${((buyCount / stocks.length) * 100).toFixed(0)}% 강세 의견`,
      icon: "📈",
      color: "#10b981",
    },
    {
      label: "평균 상승여력",
      value: `+${avgUpside.toFixed(1)}%`,
      sub: "목표주가 기준",
      icon: "📊",
      color: "#f59e0b",
    },
    {
      label: "최고 상승여력",
      value: `+${maxUpside.toFixed(1)}%`,
      sub: top1.종목명.slice(0, 10),
      icon: "🏆",
      color: "#f59e0b",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((c, i) => (
        <div
          key={i}
          className="card-glow rounded-xl p-5"
          style={{
            background: "linear-gradient(135deg,#111827,#1a2235)",
            border: `1px solid ${c.color}22`,
            animationDelay: `${i * 0.08}s`,
          }}
        >
          <div className="flex items-start justify-between mb-3">
            <p style={{ color: "#64748b" }} className="text-xs font-medium uppercase tracking-wider">
              {c.label}
            </p>
            <span className="text-xl">{c.icon}</span>
          </div>
          <p
            className="text-2xl font-bold mb-1"
            style={{ color: c.color }}
          >
            {c.value}
          </p>
          <p style={{ color: "#475569" }} className="text-xs">
            {c.sub}
          </p>
        </div>
      ))}
    </div>
  );
}
