# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Development
npm run dev       # Start local dev server at http://localhost:3000
npm run build     # Production build (must pass before deploying)
npm run lint      # ESLint check

# Deploy to Vercel (from stock-dashboard/)
vercel --prod --yes
```

## Data Pipeline

Data flows from a Python scraper outside this Next.js project:

```
/블로그/target_price_analyzer.py   →   /stock-dashboard/public/stocks.json
```

1. Run `python target_price_analyzer.py` from `/블로그/` — it scrapes https://consensus.hankyung.com/analysis/list and writes `upside_YYYYMMDD.json`.
2. Copy that file to `public/stocks.json` before building or deploying.

`stocks.json` schema:
```json
{
  "날짜": "YYYY-MM-DD",
  "종목명": "string",
  "종목코드": "6-digit string",
  "목표주가": number,
  "리포트수": number,
  "투자의견": "Buy|매수|Hold|중립|Sell|매도|투자의견없음",
  "증권사": "comma-joined string",
  "현재가": number,
  "상승여력(%)": number
}
```

## Architecture

**Next.js 16 App Router** with server-only data fetching:

- `app/page.tsx` — async server component. Reads `public/stocks.json` via `fs`, filters stocks with valid prices, slices top 10, passes to client components.
- `app/layout.tsx` — global metadata, Korean font stack.
- `app/globals.css` — CSS variables (`--accent: #f59e0b`, `--up: #10b981`, `--border: #1e3a5f`, etc.), `.card-glow`, `.gradient-text`, `.pulse-dot`, `.fade-in`, `.stock-row`.

**Components** (all in `components/`):
- `Header.tsx` — `"use client"`, real-time clock with `setInterval`.
- `StatCards.tsx` — 4 summary cards computed from stocks array.
- `UpsideChart.tsx` — Recharts `BarChart` for top 10, `Cell` colors by rank (gold/green/blue). Uses `(v: unknown)` type for `LabelList` formatter to satisfy Recharts types.
- `StockTable.tsx` — `"use client"`, sortable by 상승여력/목표주가/현재가, searchable by 종목명/종목코드/증권사.

## Key Conventions

- Dark finance theme: background `#0a0e1a`, cards `#111827`/`#1a2235`, border `#1e3a5f`, accent gold `#f59e0b`, up green `#10b981`, down red `#ef4444`.
- Inline styles are used alongside Tailwind — do not remove inline styles in favor of Tailwind classes; both coexist intentionally.
- Korean text truncation: `종목명` is sliced to 6 chars in the chart, 12 chars in the table.
- `증권사` field may contain comma-joined firm names; display only `s.증권사.split(",")[0]` in tables.

## Scraper Notes (`target_price_analyzer.py`)

- Uses `YYYY-MM-DD` date format in query params (not `YYYYMMDD`).
- Deduplicates by `종목코드`: averages 목표주가, picks majority 투자의견, joins 증권사.
- Auto-expands to yesterday's data if fewer than 10 valid stocks found today.
- `FinanceDataReader` (not yfinance) for Korean stock prices — no `.KS`/`.KQ` suffix needed.
