"use client";
import { useState } from "react";

interface ReportItem {
  증권사: string;
  제목: string;
  url: string;
}

interface Stock {
  종목명: string;
  종목코드: string;
  현재가: number;
  목표주가: number;
  "상승여력(%)": number;
  투자의견: string;
  증권사: string;
  리포트수?: number;
  리포트목록?: ReportItem[];
}

interface Props {
  stocks: Stock[];
}

const OPINION_STYLE: Record<string, { bg: string; color: string }> = {
  Buy:       { bg: "rgba(16,185,129,0.15)",  color: "#10b981" },
  매수:      { bg: "rgba(16,185,129,0.15)",  color: "#10b981" },
  Hold:      { bg: "rgba(251,191,36,0.12)",  color: "#fbbf24" },
  중립:      { bg: "rgba(251,191,36,0.12)",  color: "#fbbf24" },
  Sell:      { bg: "rgba(239,68,68,0.15)",   color: "#ef4444" },
  매도:      { bg: "rgba(239,68,68,0.15)",   color: "#ef4444" },
  투자의견없음: { bg: "rgba(100,116,139,0.15)", color: "#64748b" },
};

function opinionStyle(op: string) {
  return OPINION_STYLE[op] ?? { bg: "rgba(100,116,139,0.15)", color: "#94a3b8" };
}

export default function StockTable({ stocks }: Props) {
  const [sortKey, setSortKey] = useState<"상승여력(%)" | "목표주가" | "현재가">("상승여력(%)");
  const [search, setSearch] = useState("");
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  const filtered = stocks
    .filter(
      (s) =>
        s.종목명.includes(search) ||
        s.종목코드.includes(search) ||
        s.증권사.includes(search)
    )
    .sort((a, b) => b[sortKey] - a[sortKey]);

  const headers: { key: "상승여력(%)" | "목표주가" | "현재가"; label: string }[] = [
    { key: "상승여력(%)", label: "상승여력" },
    { key: "목표주가", label: "목표주가" },
    { key: "현재가", label: "현재가" },
  ];

  return (
    <div
      className="card-glow rounded-xl overflow-hidden"
      style={{ background: "linear-gradient(135deg,#111827,#1a2235)", border: "1px solid #1e3a5f" }}
    >
      {/* 헤더 */}
      <div
        className="px-6 py-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
        style={{ borderBottom: "1px solid #1e3a5f" }}
      >
        <div>
          <h2 className="text-white font-bold text-lg">전체 종목 리스트</h2>
          <p style={{ color: "#64748b" }} className="text-xs mt-0.5">
            {filtered.length}개 종목
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* 검색 */}
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">🔍</span>
            <input
              type="text"
              placeholder="종목명 / 증권사 검색"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-2 text-sm rounded-lg text-white placeholder-gray-600 outline-none"
              style={{ background: "#0a0e1a", border: "1px solid #1e3a5f", width: 180 }}
            />
          </div>

          {/* 정렬 */}
          <div className="flex gap-1">
            {headers.map((h) => (
              <button
                key={h.key}
                onClick={() => setSortKey(h.key)}
                className="text-xs px-3 py-1.5 rounded-lg font-medium transition-all"
                style={
                  sortKey === h.key
                    ? { background: "rgba(245,158,11,0.2)", color: "#f59e0b", border: "1px solid rgba(245,158,11,0.4)" }
                    : { background: "transparent", color: "#64748b", border: "1px solid #1e3a5f" }
                }
              >
                {h.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 테이블 */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr style={{ background: "#0d1424", borderBottom: "1px solid #1e3a5f" }}>
              {["순위", "종목명", "종목코드", "현재가", "목표주가", "상승여력", "투자의견", "증권사"].map((h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                  style={{ color: "#64748b" }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((s, i) => {
              const upside = s["상승여력(%)"];
              const op = opinionStyle(s.투자의견);
              const isTop = i === 0;

              return (
                <tr
                  key={s.종목코드}
                  className="stock-row"
                  style={{
                    borderBottom: "1px solid rgba(30,58,95,0.5)",
                    background: isTop ? "rgba(245,158,11,0.04)" : "transparent",
                  }}
                >
                  {/* 순위 */}
                  <td className="px-4 py-4">
                    <span
                      className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                      style={
                        isTop
                          ? { background: "#f59e0b", color: "#000" }
                          : i < 3
                          ? { background: "rgba(245,158,11,0.15)", color: "#f59e0b" }
                          : { background: "#1a2235", color: "#64748b" }
                      }
                    >
                      {i + 1}
                    </span>
                  </td>

                  {/* 종목명 */}
                  <td className="px-4 py-4">
                    <div className="relative inline-block">
                      {s.리포트목록?.length === 1 ? (
                        // 리포트 1개: 바로 링크
                        <a
                          href={s.리포트목록[0].url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-semibold hover:underline"
                          style={{ color: "#e2e8f0" }}
                          title={s.리포트목록[0].제목}
                        >
                          {s.종목명.length > 12 ? s.종목명.slice(0, 12) + "…" : s.종목명}
                          <span className="ml-1.5 text-xs" style={{ color: "#3b82f6" }}>↓</span>
                        </a>
                      ) : s.리포트목록?.length! > 1 ? (
                        // 리포트 여러 개: 드롭다운
                        <>
                          <button
                            onClick={() => setOpenDropdown(openDropdown === s.종목코드 ? null : s.종목코드)}
                            className="font-semibold text-left"
                            style={{ color: "#e2e8f0" }}
                          >
                            {s.종목명.length > 12 ? s.종목명.slice(0, 12) + "…" : s.종목명}
                            <span
                              className="ml-1.5 text-xs px-1.5 py-0.5 rounded-full font-bold"
                              style={{ background: "rgba(59,130,246,0.2)", color: "#3b82f6" }}
                            >
                              {s.리포트목록!.length}↓
                            </span>
                          </button>
                          {openDropdown === s.종목코드 && (
                            <div
                              className="absolute left-0 top-full mt-1 z-50 rounded-lg overflow-hidden text-xs"
                              style={{
                                background: "#1a2235",
                                border: "1px solid #1e3a5f",
                                minWidth: 220,
                                boxShadow: "0 8px 24px rgba(0,0,0,0.5)",
                              }}
                            >
                              {s.리포트목록!.map((r, idx) => (
                                <a
                                  key={idx}
                                  href={r.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-2 px-3 py-2.5 hover:bg-white/5"
                                  style={{ color: "#94a3b8", borderBottom: idx < s.리포트목록!.length - 1 ? "1px solid #1e3a5f" : "none" }}
                                  onClick={() => setOpenDropdown(null)}
                                >
                                  <span style={{ color: "#3b82f6" }}>↓</span>
                                  <span style={{ color: "#f59e0b", whiteSpace: "nowrap" }}>{r.증권사}</span>
                                  <span className="truncate">{r.제목 || "리포트 보기"}</span>
                                </a>
                              ))}
                            </div>
                          )}
                        </>
                      ) : (
                        // 리포트 없음
                        <span className="font-semibold text-white">
                          {s.종목명.length > 12 ? s.종목명.slice(0, 12) + "…" : s.종목명}
                        </span>
                      )}
                    </div>
                    {isTop && (
                      <span
                        className="ml-2 text-xs px-1.5 py-0.5 rounded"
                        style={{ background: "rgba(245,158,11,0.2)", color: "#f59e0b" }}
                      >
                        TOP
                      </span>
                    )}
                  </td>

                  {/* 종목코드 */}
                  <td className="px-4 py-4">
                    <span
                      className="font-mono text-xs px-2 py-1 rounded"
                      style={{ background: "#0a0e1a", color: "#94a3b8" }}
                    >
                      {s.종목코드}
                    </span>
                  </td>

                  {/* 현재가 */}
                  <td className="px-4 py-4 font-mono" style={{ color: "#94a3b8" }}>
                    {s.현재가.toLocaleString()}
                    <span className="text-xs ml-0.5" style={{ color: "#475569" }}>원</span>
                  </td>

                  {/* 목표주가 */}
                  <td className="px-4 py-4 font-mono font-semibold" style={{ color: "#fbbf24" }}>
                    {s.목표주가.toLocaleString()}
                    <span className="text-xs ml-0.5" style={{ color: "#78716c" }}>원</span>
                  </td>

                  {/* 상승여력 */}
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <span
                        className="font-bold text-sm"
                        style={{ color: upside >= 0 ? "#10b981" : "#ef4444" }}
                      >
                        {upside >= 0 ? "+" : ""}{upside.toFixed(2)}%
                      </span>
                      {/* 게이지 바 */}
                      <div
                        className="h-1.5 rounded-full flex-1 min-w-[40px] max-w-[80px]"
                        style={{ background: "#1e3a5f" }}
                      >
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${Math.min(Math.abs(upside) / 1.5, 100)}%`,
                            background: upside >= 0 ? "#10b981" : "#ef4444",
                          }}
                        />
                      </div>
                    </div>
                  </td>

                  {/* 투자의견 */}
                  <td className="px-4 py-4">
                    <span
                      className="text-xs px-2.5 py-1 rounded-full font-semibold"
                      style={{ background: op.bg, color: op.color }}
                    >
                      {s.투자의견}
                    </span>
                  </td>

                  {/* 증권사 */}
                  <td className="px-4 py-4 text-xs" style={{ color: "#64748b" }}>
                    {s.증권사.split(",")[0]}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* 면책 고지 */}
      <div
        className="px-6 py-3 text-xs"
        style={{ borderTop: "1px solid #1e3a5f", color: "#334155" }}
      >
        ※ 본 자료는 한경컨센서스 기업 리포트를 기반으로 자동 집계된 참고 자료입니다. 투자 판단의 책임은 본인에게 있습니다.
      </div>
    </div>
  );
}
