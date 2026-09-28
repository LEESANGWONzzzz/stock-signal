#!/usr/bin/env python3
"""
크림(KREAM) / 포이즌(Poizon·Dewu) 리셀 시세 조회기
- Apify 무료 플랜(월 $5 크레딧, 카드 등록 불필요) 으로 실행
- KREAM  : abotapi/kream-scraper           (키워드 검색)
- Poizon : sian.agency/dewu-poizon-price-tracker (품번 검색)

사용법
  1) https://console.apify.com 가입 → Settings > Integrations 에서 API 토큰 복사
  2) export APIFY_TOKEN="apify_api_xxx"
  3) python resell_price.py kream "나이키 덩크 로우"
     python resell_price.py poizon DD1391-100
     python resell_price.py both DD1391-100      # 같은 품번으로 두 곳 비교

결과는 화면에 요약 출력 + resell_<플랫폼>_<YYYYMMDD_HHMMSS>.json 으로 원본 저장.
"""

import os
import sys
import json
import argparse
from datetime import datetime

import requests

APIFY_BASE = "https://api.apify.com/v2"
KREAM_ACTOR = "abotapi~kream-scraper"
POIZON_ACTOR = "sian.agency~dewu-poizon-price-tracker"

# Actor 마다 출력 필드 이름이 달라서, 후보 키를 순서대로 찾아 표시한다.
FIELD_CANDIDATES = {
    "name":   ["name", "title", "productName", "translatedName", "nameKo"],
    "code":   ["styleCode", "style_code", "modelNumber", "articleNumber", "sku"],
    "lowest": ["lowestAsk", "lowest_ask", "lowestPrice", "minPrice", "price", "marketPrice"],
    "bid":    ["highestBid", "highest_bid", "maxBid"],
    "retail": ["retailPrice", "retail_price", "releasePrice", "originalPrice"],
    "url":    ["url", "productUrl", "link"],
}


# ── Apify 호출 ────────────────────────────────────────────────────────────────

def run_actor(actor: str, actor_input: dict, token: str) -> list[dict]:
    """Actor 를 동기 실행하고 결과 데이터셋을 그대로 반환 (최대 5분 대기)."""
    url = f"{APIFY_BASE}/acts/{actor}/run-sync-get-dataset-items"
    resp = requests.post(
        url,
        json=actor_input,
        headers={"Authorization": f"Bearer {token}"},
        timeout=320,
    )
    if resp.status_code == 402:
        raise SystemExit("❌ Apify 무료 크레딧을 모두 썼습니다. 다음 달에 초기화됩니다.")
    if resp.status_code == 401:
        raise SystemExit("❌ APIFY_TOKEN 이 올바르지 않습니다.")
    resp.raise_for_status()
    return resp.json()


def search_kream(keyword: str, limit: int, token: str) -> list[dict]:
    return run_actor(KREAM_ACTOR, {
        "mode": "search",
        "keywords": [keyword],
        "maxItems": limit,
    }, token)


def search_poizon(style_code: str, limit: int, token: str) -> list[dict]:
    return run_actor(POIZON_ACTOR, {
        "styleCodes": [style_code],
        "maxResultsPerQuery": limit,
    }, token)


# ── 출력 ──────────────────────────────────────────────────────────────────────

def pick(item: dict, key: str):
    for k in FIELD_CANDIDATES[key]:
        v = item.get(k)
        if v not in (None, ""):
            return v
    return "-"


def fmt_price(v) -> str:
    if isinstance(v, (int, float)):
        return f"{v:,.0f}"
    return str(v)


def print_table(platform: str, items: list[dict]) -> None:
    print(f"\n📦 {platform} — {len(items)}건")
    if not items:
        print("  결과 없음")
        return
    print(f"  {'상품명':<40} {'품번':<14} {'최저판매가':>12} {'최고구매가':>12} {'발매가':>12}")
    print("  " + "-" * 94)
    for it in items:
        name = str(pick(it, "name"))[:38]
        print(
            f"  {name:<40} {str(pick(it, 'code')):<14} "
            f"{fmt_price(pick(it, 'lowest')):>12} {fmt_price(pick(it, 'bid')):>12} "
            f"{fmt_price(pick(it, 'retail')):>12}"
        )
    # 필드 매핑이 틀렸을 때 원본 키를 확인할 수 있게 첫 항목의 키 목록 표시
    print(f"  (원본 필드: {', '.join(list(items[0].keys())[:15])} ...)")


def save_json(platform: str, items: list[dict]) -> str:
    path = f"resell_{platform}_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return path


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="크림/포이즌 리셀 시세 조회 (Apify 무료 플랜)")
    parser.add_argument("platform", choices=["kream", "poizon", "both"])
    parser.add_argument("query", help="크림: 검색어 또는 품번 / 포이즌: 품번 (예: DD1391-100)")
    parser.add_argument("--limit", type=int, default=5, help="최대 결과 수 (크레딧 절약, 기본 5)")
    args = parser.parse_args()

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("❌ 환경변수 APIFY_TOKEN 을 설정하세요. (console.apify.com > Settings > Integrations)")

    jobs = []
    if args.platform in ("kream", "both"):
        jobs.append(("kream", search_kream))
    if args.platform in ("poizon", "both"):
        jobs.append(("poizon", search_poizon))

    for platform, fn in jobs:
        print(f"🔍 {platform} 에서 '{args.query}' 조회 중... (최대 5분 소요)")
        try:
            items = fn(args.query, args.limit, token)
        except requests.RequestException as e:
            print(f"❌ {platform} 조회 실패: {e}")
            continue
        print_table(platform, items)
        print(f"  💾 원본 저장: {save_json(platform, items)}")


if __name__ == "__main__":
    main()
