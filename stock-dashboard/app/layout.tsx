import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "증권 리포트 대시보드 | 목표주가 상승여력 TOP 10",
  description: "한경컨센서스 기반 오늘의 증권사 리포트를 분석해 목표주가 상승여력 상위 종목을 실시간으로 보여주는 전문 대시보드",
  keywords: "주식, 증권리포트, 목표주가, 상승여력, 한경컨센서스, 주식투자",
  openGraph: {
    title: "증권 리포트 대시보드 | 목표주가 상승여력 TOP 10",
    description: "오늘의 증권사 리포트 — 상승여력 TOP 10 종목",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
