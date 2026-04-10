"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from "recharts";

interface Stock {
  종목명: string;
  종목코드: string;
  "상승여력(%)": number;
  투자의견: string;
}

interface Props {
  stocks: Stock[];
}

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div
      style={{
        background: "#1a2235",
        border: "1px solid #1e3a5f",
        borderRadius: 8,
        padding: "10px 14px",
        fontSize: 13,
      }}
    >
      <p style={{ color: "#f59e0b", fontWeight: 700 }}>{d.종목명}</p>
      <p style={{ color: "#10b981", marginTop: 4 }}>
        상승여력: <strong>+{d["상승여력(%)"].toFixed(1)}%</strong>
      </p>
      <p style={{ color: "#64748b", fontSize: 11, marginTop: 2 }}>
        {d.투자의견}
      </p>
    </div>
  );
};

export default function UpsideChart({ stocks }: Props) {
  const data = [...stocks]
    .sort((a, b) => b["상승여력(%)"] - a["상승여력(%)"])
    .slice(0, 10)
    .map((s) => ({
      ...s,
      종목명: s.종목명.slice(0, 6),
    }));

  return (
    <div
      className="card-glow rounded-xl p-6 mb-8"
      style={{ background: "linear-gradient(135deg,#111827,#1a2235)", border: "1px solid #1e3a5f" }}
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-white font-bold text-lg">상승여력 분포</h2>
          <p style={{ color: "#64748b" }} className="text-xs mt-0.5">
            상위 10종목 · 목표주가 기준
          </p>
        </div>
        <span
          style={{
            background: "rgba(16,185,129,0.15)",
            color: "#10b981",
            border: "1px solid rgba(16,185,129,0.3)",
          }}
          className="text-xs px-3 py-1 rounded-full font-medium"
        >
          BarChart
        </span>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 20, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" vertical={false} />
          <XAxis
            dataKey="종목명"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#64748b", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
          <Bar dataKey="상승여력(%)" radius={[6, 6, 0, 0]} maxBarSize={52}>
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={
                  index === 0
                    ? "#f59e0b"
                    : index === 1
                    ? "#fbbf24"
                    : index === 2
                    ? "#10b981"
                    : "#3b82f6"
                }
                fillOpacity={index === 0 ? 1 : 0.75}
              />
            ))}
            <LabelList
              dataKey="상승여력(%)"
              position="top"
              formatter={(v: unknown) => `+${Number(v).toFixed(0)}%`}
              style={{ fill: "#94a3b8", fontSize: 11 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
