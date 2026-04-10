#!/usr/bin/env python3
"""
한경컨센서스 상승여력 분석기 v2
- BeautifulSoup 으로 기업 리포트 스크래핑
- FinanceDataReader 로 현재가 조회 (한국 주식 전용)
- 상승여력(%) = (목표주가 - 현재가) / 현재가 × 100
- 상위 10종목 표 출력
"""

import re
import json
import warnings
from datetime import datetime, timedelta
from collections import defaultdict, Counter

import requests
from bs4 import BeautifulSoup
import FinanceDataReader as fdr

warnings.filterwarnings("ignore")

BASE_URL = "https://consensus.hankyung.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://consensus.hankyung.com/",
}

# ── 숫자 추출 헬퍼 ─────────────────────────────────────────────────────────────

def extract_number(text: str) -> int:
    """
    텍스트에서 쉼표·공백·단위 문자를 제거하고 정수만 추출.
    숫자가 없거나 0이면 0 반환.
    예) "50,000원" → 50000 / "N/A" → 0 / "- " → 0
    """
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else 0


# ── 제목 정제 ──────────────────────────────────────────────────────────────────

def clean_title(raw: str) -> str:
    """
    한경컨센서스 <td> 안에는 제목이 본문+툴팁 형태로 중복 삽입됨.
    → a 태그 텍스트를 우선 사용하고, 종목코드 괄호 제거.
    예) "GS건설(006360) 올랐어도 또 오른다" → "GS건설 올랐어도 또 오른다"
    """
    title = re.sub(r"\(\d{6}\)", "", raw).strip()
    # 연속 공백 정리
    title = re.sub(r"\s{2,}", " ", title)
    return title


# ── 스크래핑 ──────────────────────────────────────────────────────────────────

def fetch_business_page(session: requests.Session, sdate: str, edate: str,
                        page: int, page_size: int = 80) -> BeautifulSoup:
    url = (
        f"{BASE_URL}/analysis/list"
        f"?skinType=business"
        f"&sdate={sdate}&edate={edate}"
        f"&pagenum={page_size}&now_page={page}"
    )
    resp = session.get(url, headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def scrape_reports(sdate: str, edate: str) -> tuple[list[dict], dict]:
    """
    기업 탭 전체 페이지를 순회하며 리포트 수집.
    Returns (raw_records, log_stats)
    """
    session = requests.Session()
    raw: list[dict] = []
    stats = {"total_rows": 0, "skip_no_code": 0, "skip_zero_target": 0}
    page = 1

    while True:
        soup = fetch_business_page(session, sdate, edate, page)
        tbody = soup.find("tbody")
        if not tbody:
            break

        rows = tbody.find_all("tr")
        batch_count = 0

        for tr in rows:
            if "listNone" in tr.get("class", []):
                continue
            cells = tr.find_all("td")
            if len(cells) < 6:
                continue

            stats["total_rows"] += 1

            date_txt     = cells[0].get_text(strip=True)
            title_td     = cells[1]
            target_txt   = cells[2].get_text(strip=True)
            opinion_txt  = cells[3].get_text(strip=True)
            analyst_txt  = cells[4].get_text(strip=True)
            source_txt   = cells[5].get_text(strip=True)

            # 제목: a 태그 텍스트 우선
            a_tag = title_td.find("a")
            full_title = a_tag.get_text(strip=True) if a_tag else title_td.get_text(strip=True)

            # 종목코드 추출
            code_m = re.search(r"\((\d{6})\)", full_title)
            if not code_m:
                stats["skip_no_code"] += 1
                continue
            stock_code = code_m.group(1)
            stock_name = clean_title(full_title)

            # 목표주가 추출 (정규식)
            target_price = extract_number(target_txt)
            if target_price <= 0:
                stats["skip_zero_target"] += 1
                continue

            raw.append({
                "날짜":     date_txt,
                "종목명":    stock_name,
                "종목코드":   stock_code,
                "목표주가":   target_price,
                "투자의견":   opinion_txt.strip(),
                "작성자":    analyst_txt,
                "증권사":    source_txt,
            })
            batch_count += 1

        if batch_count == 0:
            break

        # 마지막 페이지 확인
        page_links = soup.select("div.paging a")
        page_nums = [
            int(m.group(1))
            for a in page_links
            if (m := re.search(r"now_page=(\d+)", a.get("href", "")))
        ]
        last_page = max(page_nums) if page_nums else page
        if page >= last_page:
            break
        page += 1

    return raw, stats


# ── 중복 제거 (종목코드 기준) ────────────────────────────────────────────────

def deduplicate(records: list[dict]) -> list[dict]:
    grouped: dict[str, list] = defaultdict(list)
    for r in records:
        grouped[r["종목코드"]].append(r)

    result = []
    for code, items in grouped.items():
        avg_price = round(sum(i["목표주가"] for i in items) / len(items))
        opinions  = Counter(i["투자의견"] for i in items)
        firms     = list(dict.fromkeys(i["증권사"] for i in items))
        result.append({
            "날짜":     items[0]["날짜"],
            "종목명":    items[0]["종목명"],
            "종목코드":   code,
            "목표주가":   avg_price,
            "리포트수":   len(items),
            "투자의견":   opinions.most_common(1)[0][0],
            "증권사":    ", ".join(firms),
        })
    return result


# ── 현재가 조회 (FinanceDataReader) ──────────────────────────────────────────

_PRICE_CACHE: dict[str, float] = {}

def get_current_price(code: str, ref_date: str) -> float:
    """
    FinanceDataReader 로 종목코드의 최근 종가 조회.
    ref_date 기준 5거래일 데이터를 내려받아 마지막 종가 사용.
    조회 실패 시 0.0 반환.
    """
    if code in _PRICE_CACHE:
        return _PRICE_CACHE[code]

    try:
        # ref_date 포함 최근 5거래일
        start = (datetime.strptime(ref_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
        df = fdr.DataReader(code, start, ref_date)
        if df is not None and not df.empty and "Close" in df.columns:
            price = float(df["Close"].iloc[-1])
            _PRICE_CACHE[code] = price
            return price
    except Exception:
        pass

    _PRICE_CACHE[code] = 0.0
    return 0.0


# ── 상승여력 계산 ─────────────────────────────────────────────────────────────

def calc_upside(records: list[dict], ref_date: str) -> tuple[list[dict], int]:
    """Returns (enriched_list, count_no_price)"""
    enriched = []
    no_price = 0
    total = len(records)

    for i, r in enumerate(records, 1):
        code = r["종목코드"]
        print(f"  [{i:>2}/{total}] {r['종목명'][:20]:<20} ({code}) 현재가 조회...", end="\r")
        price = get_current_price(code, ref_date)

        if price <= 0:
            no_price += 1
            continue

        upside = (r["목표주가"] - price) / price * 100
        enriched.append({
            **r,
            "현재가":      round(price),
            "상승여력(%)":  round(upside, 2),
        })

    print(" " * 70, end="\r")  # 진행 줄 지우기
    return enriched, no_price


# ── 터미널 표 출력 ─────────────────────────────────────────────────────────────

def print_table(rows: list[dict], top_n: int = 10):
    sorted_rows = sorted(rows, key=lambda x: x["상승여력(%)"], reverse=True)[:top_n]

    cols   = ["순위", "종목명", "코드", "현재가", "목표주가", "상승여력", "의견", "증권사"]
    widths = [4,      18,       8,     10,       10,        10,        8,     22]

    def row_str(vals):
        return "| " + " | ".join(f"{v:<{w}}" for v, w in zip(vals, widths)) + " |"

    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(sep)
    print(row_str(cols))
    print(sep)
    for rank, r in enumerate(sorted_rows, 1):
        row = [
            str(rank),
            r["종목명"][:widths[1]],
            r["종목코드"],
            f"{r['현재가']:,}",
            f"{r['목표주가']:,}",
            f"{r['상승여력(%)']:+.2f}%",
            r["투자의견"][:widths[6]],
            r["증권사"][:widths[7]],
        ]
        print(row_str(row))
    print(sep)


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    today     = datetime.today()
    today_str = today.strftime("%Y-%m-%d")
    yest_str  = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    print("=" * 80)
    print(f"  한경컨센서스 상승여력 분석기 v2  |  기준일: {today_str}")
    print("=" * 80)

    # ── Step 1 : 스크래핑 (오늘 → 부족하면 어제까지 확장) ─────────────────
    print(f"\n▶ Step 1 | 리포트 스크래핑")

    raw, stats = scrape_reports(today_str, today_str)
    deduped = deduplicate(raw)

    print(f"\n  [스크래핑 로그]")
    print(f"  ├ 전체 행 수집         : {stats['total_rows']:>4}건")
    print(f"  ├ 종목코드 없어 제외    : {stats['skip_no_code']:>4}건")
    print(f"  ├ 목표주가 0 이어서 제외 : {stats['skip_zero_target']:>4}건")
    print(f"  └ 유효 리포트          : {len(raw):>4}건  →  {len(deduped)}종목 (중복 제거 후)")

    # 유효 종목 10개 미만이면 어제 데이터 추가
    if len(deduped) < 10:
        print(f"\n  ⚠  유효 종목 {len(deduped)}개 < 10개 → 어제({yest_str}) 데이터 추가 수집")
        raw2, stats2 = scrape_reports(yest_str, yest_str)

        # 이미 수집된 종목코드 중복 방지
        existing_codes = {r["종목코드"] for r in raw}
        new_raw = [r for r in raw2 if r["종목코드"] not in existing_codes]
        raw.extend(new_raw)
        deduped = deduplicate(raw)

        print(f"  [어제 추가 로그]")
        print(f"  ├ 추가 전체 행        : {stats2['total_rows']:>4}건")
        print(f"  ├ 신규 추가 리포트     : {len(new_raw):>4}건")
        print(f"  └ 합산 유효 종목       : {len(deduped):>4}개")

    # ── Step 2 : 현재가 조회 ────────────────────────────────────────────────
    print(f"\n▶ Step 2 | 현재가 조회 (FinanceDataReader · KRX)")
    enriched, no_price = calc_upside(deduped, today_str)

    print(f"  [현재가 조회 로그]")
    print(f"  ├ 조회 시도   : {len(deduped):>4}종목")
    print(f"  ├ 조회 실패   : {no_price:>4}종목  (현재가 N/A → 제외)")
    print(f"  └ 최종 유효   : {len(enriched):>4}종목")

    if len(enriched) == 0:
        print("\n  ⚠  유효 데이터가 없습니다. 장 마감 후 시간 외 조회 또는 공휴일일 수 있습니다.")
        return

    # ── Step 3 : 결과 출력 ──────────────────────────────────────────────────
    top_n = min(10, len(enriched))
    print(f"\n▶ Step 3 | 상승여력 상위 {top_n}종목")
    print(f"  공식: ((목표주가 - 현재가) / 현재가) × 100\n")
    print_table(enriched, top_n=top_n)

    # ── Step 4 : JSON 저장 ──────────────────────────────────────────────────
    filename = f"upside_{today_str.replace('-','')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            sorted(enriched, key=lambda x: x["상승여력(%)"], reverse=True),
            f, ensure_ascii=False, indent=2
        )
    print(f"\n✅ 전체 결과 저장 → {filename}  ({len(enriched)}종목)")
    print("=" * 80)


if __name__ == "__main__":
    main()
