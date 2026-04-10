#!/usr/bin/env python3
"""
인스타그램 카드뉴스 생성기 (1080×1080)
- card_1.png : 표지
- card_2.png : 2~5위 미끼 본문
- card_3.png : CTA (전환 유도)
데이터 소스: upside_YYYYMMDD.json (target_price_analyzer.py 출력)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── 색상 팔레트 ─────────────────────────────────────────────────────────────
C_BG          = "#1A237E"   # 어두운 남색 배경
C_BG_CARD     = "#1E2D8F"   # 카드 내부 (약간 밝은 남색)
C_ACCENT      = "#FFC107"   # 노란색 강조
C_ACCENT2     = "#FFD54F"   # 연한 노란색
C_WHITE       = "#FFFFFF"
C_GREY        = "#B0BEC5"
C_UP          = "#69F0AE"   # 상승 초록
C_DIVIDER     = "#3949AB"   # 구분선
C_HEADER_BG   = "#283593"   # 표 헤더 배경
C_ROW_ALT     = "#1C2980"   # 짝수 행 배경
C_OVERLAY     = (0, 0, 0, 80)  # 반투명 오버레이

SIZE = (1080, 1080)
MARGIN = 60


# ── 폰트 로더 ─────────────────────────────────────────────────────────────────

def find_korean_font() -> str:
    """시스템에서 한글 지원 폰트 경로를 자동 탐색."""
    candidates = [
        # macOS
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/System/Library/Fonts/Supplemental/NotoSansGothic-Regular.ttf",
        # Windows
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc",
        # Linux (NanumGothic)
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/nanum/NanumGothic.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "한글 폰트를 찾을 수 없습니다. "
        "NanumGothic 또는 AppleGothic 등을 설치해 주세요."
    )


def load_fonts(base_path: str) -> dict:
    """폰트 크기별 dict 반환. TTC는 index=0 지정."""
    is_ttc = base_path.endswith(".ttc")

    def load(size):
        return ImageFont.truetype(base_path, size, index=0) if is_ttc \
               else ImageFont.truetype(base_path, size)

    return {
        "xl":   load(64),   # 초대형 제목
        "lg":   load(48),   # 대형
        "md":   load(36),   # 중형
        "sm":   load(28),   # 소형
        "xs":   load(22),   # 극소형
        "tiny": load(18),   # 최소
    }


# ── 공통 드로잉 유틸 ──────────────────────────────────────────────────────────

def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def draw_rounded_rect(draw: ImageDraw, xy, radius: int, fill: str, outline: str = None):
    x1, y1, x2, y2 = xy
    fill_rgb = hex_to_rgb(fill)
    draw.rounded_rectangle(xy, radius=radius, fill=fill_rgb,
                           outline=hex_to_rgb(outline) if outline else None,
                           width=2 if outline else 0)


def draw_text_centered(draw: ImageDraw, text: str, y: int, font,
                       color: str, width: int = SIZE[0]):
    rgb = hex_to_rgb(color)
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    x = (width - w) // 2
    draw.text((x, y), text, font=font, fill=rgb)


def draw_gradient_bg(img: Image.Image):
    """위→아래 남색 그라디언트 배경."""
    draw = ImageDraw.Draw(img)
    top    = hex_to_rgb("#0D1457")
    bottom = hex_to_rgb("#1A237E")
    for y in range(SIZE[1]):
        r = int(top[0] + (bottom[0] - top[0]) * y / SIZE[1])
        g = int(top[1] + (bottom[1] - top[1]) * y / SIZE[1])
        b = int(top[2] + (bottom[2] - top[2]) * y / SIZE[1])
        draw.line([(0, y), (SIZE[0], y)], fill=(r, g, b))


def draw_decorative_lines(draw: ImageDraw):
    """배경 장식선 (대각 + 수평)."""
    a = hex_to_rgb(C_DIVIDER)
    # 대각 장식
    for i in range(0, SIZE[0] + SIZE[1], 120):
        draw.line([(i, 0), (0, i)], fill=(*a, 30), width=1)
    # 상단 강조선
    draw.line([(MARGIN, 30), (SIZE[0] - MARGIN, 30)],
              fill=hex_to_rgb(C_ACCENT), width=3)
    # 하단 강조선
    draw.line([(MARGIN, SIZE[1] - 30), (SIZE[0] - MARGIN, SIZE[1] - 30)],
              fill=hex_to_rgb(C_ACCENT), width=3)


def draw_logo_badge(draw: ImageDraw, fonts: dict):
    """우하단 워터마크 배지."""
    badge_text = "한경컨센서스 분석"
    bbox = fonts["tiny"].getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 24
    bh = bbox[3] - bbox[1] + 12
    x = SIZE[0] - MARGIN - bw
    y = SIZE[1] - MARGIN - bh + 10
    draw_rounded_rect(draw, (x, y, x + bw, y + bh), 8, C_HEADER_BG, C_DIVIDER)
    draw.text((x + 12, y + 6), badge_text,
              font=fonts["tiny"], fill=hex_to_rgb(C_GREY))


# ── 카드 1: 표지 ──────────────────────────────────────────────────────────────

def make_card1(fonts: dict, today_str: str) -> Image.Image:
    img = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient_bg(img)
    draw_decorative_lines(draw)

    # 중앙 박스
    bx1, by1 = MARGIN + 20, 240
    bx2, by2 = SIZE[0] - MARGIN - 20, 760
    draw_rounded_rect(draw, (bx1, by1, bx2, by2), 24, C_BG_CARD, C_DIVIDER)

    # 상단 태그
    tag = "📊 증권사 리포트 분석"
    draw_text_centered(draw, tag, by1 + 40, fonts["sm"], C_ACCENT)

    # 구분선
    lx = (bx1 + bx2) // 2
    draw.line([(bx1 + 60, by1 + 90), (bx2 - 60, by1 + 90)],
              fill=hex_to_rgb(C_DIVIDER), width=2)

    # 메인 제목 (2줄)
    title1 = "목표주가 상승 여력"
    title2 = "TOP 10"
    draw_text_centered(draw, title1, by1 + 120, fonts["xl"], C_WHITE)
    draw_text_centered(draw, title2, by1 + 200, fonts["xl"], C_ACCENT)

    # 서브 제목
    sub = "오늘의 증권사 리포트 요약"
    draw_text_centered(draw, sub, by1 + 310, fonts["md"], C_GREY)

    # 날짜 배지
    date_text = f"📅  {today_str}"
    bbox = fonts["sm"].getbbox(date_text)
    dw = bbox[2] - bbox[0] + 40
    dh = 50
    dx = (SIZE[0] - dw) // 2
    dy = by1 + 390
    draw_rounded_rect(draw, (dx, dy, dx + dw, dy + dh), 25, C_ACCENT, None)
    draw.text((dx + 20, dy + 10), date_text,
              font=fonts["sm"], fill=hex_to_rgb("#1A237E"))

    # 하단 설명
    desc = "* 한경컨센서스 기업 리포트 기준"
    draw_text_centered(draw, desc, by2 + 30, fonts["xs"], C_GREY)

    # 주의 문구
    warn = "본 자료는 투자 참고용이며, 투자 판단의 책임은 본인에게 있습니다."
    draw_text_centered(draw, warn, SIZE[1] - 80, fonts["tiny"], C_GREY)

    draw_logo_badge(draw, fonts)
    return img


# ── 카드 2: 2~5위 본문 ────────────────────────────────────────────────────────

def make_card2(fonts: dict, data: list[dict], today_str: str) -> Image.Image:
    img = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient_bg(img)
    draw_decorative_lines(draw)

    # 상단 헤더
    draw_text_centered(draw, "📈 상승여력 TOP 10", 55, fonts["lg"], C_ACCENT)
    draw_text_centered(draw, f"2위 ~ 5위  |  {today_str}", 118, fonts["xs"], C_GREY)

    # 1위 티저 배너
    bx1, by1 = MARGIN, 165
    bx2, by2 = SIZE[0] - MARGIN, 215
    draw_rounded_rect(draw, (bx1, by1, bx2, by2), 12, "#FF6F00", None)
    draw_text_centered(draw, "🏆  1위 종목은 3번째 카드에서 공개!  🏆",
                       by1 + 8, fonts["sm"], C_WHITE)

    # 표 헤더
    tx1 = MARGIN
    tx2 = SIZE[0] - MARGIN
    row_h   = 148
    hdr_top = 232

    col_x   = [tx1, tx1 + 100, tx1 + 380, tx1 + 570, tx1 + 760]
    col_labels = ["순위", "종목명", "현재가", "목표주가", "상승여력"]

    draw_rounded_rect(draw, (tx1, hdr_top, tx2, hdr_top + 52), 10, C_HEADER_BG, C_DIVIDER)
    col_widths = [100, 280, 190, 190, 200]
    for i, label in enumerate(col_labels):
        cx = col_x[i] + col_widths[i] // 2
        bbox = fonts["xs"].getbbox(label)
        lw = bbox[2] - bbox[0]
        draw.text((col_x[i] + (col_widths[i] - lw) // 2, hdr_top + 14),
                  label, font=fonts["xs"], fill=hex_to_rgb(C_ACCENT))

    # 데이터 행 (2~5위 = index 1~4)
    rows_data = data[1:5]
    for i, r in enumerate(rows_data):
        rank    = i + 2
        ry      = hdr_top + 52 + i * row_h
        row_bg  = C_BG_CARD if i % 2 == 0 else C_ROW_ALT

        draw_rounded_rect(draw, (tx1, ry, tx2, ry + row_h), 0, row_bg, None)
        # 행 구분선
        draw.line([(tx1, ry + row_h), (tx2, ry + row_h)],
                  fill=hex_to_rgb(C_DIVIDER), width=1)

        cell_data = [
            (f"{rank}위",      fonts["md"],  C_ACCENT,  col_widths[0]),
            (r["종목명"][:8],   fonts["sm"],  C_WHITE,   col_widths[1]),
            (f"{r['현재가']:,}", fonts["sm"],  C_GREY,    col_widths[2]),
            (f"{r['목표주가']:,}",fonts["sm"], C_ACCENT2, col_widths[3]),
            (f"+{r['상승여력(%)']:.1f}%", fonts["md"], C_UP, col_widths[4]),
        ]
        for j, (text, fnt, color, cw) in enumerate(cell_data):
            bbox = fnt.getbbox(text)
            tw = bbox[2] - bbox[0]
            cx = col_x[j] + (cw - tw) // 2
            cy = ry + (row_h - (bbox[3] - bbox[1])) // 2
            draw.text((cx, cy), text, font=fnt, fill=hex_to_rgb(color))

    # 하단 안내
    note_y = hdr_top + 52 + 4 * row_h + 20
    draw_text_centered(draw, "▼  1위 종목이 궁금하다면 다음 카드를 확인하세요  ▼",
                       note_y, fonts["xs"], C_ACCENT)

    draw.line([(MARGIN, SIZE[1] - 55), (SIZE[0] - MARGIN, SIZE[1] - 55)],
              fill=hex_to_rgb(C_DIVIDER), width=1)
    warn = "본 자료는 투자 참고용이며, 투자 판단의 책임은 본인에게 있습니다."
    draw_text_centered(draw, warn, SIZE[1] - 45, fonts["tiny"], C_GREY)

    draw_logo_badge(draw, fonts)
    return img


# ── 카드 3: CTA ───────────────────────────────────────────────────────────────

def make_card3(fonts: dict, data: list[dict], today_str: str) -> Image.Image:
    img = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient_bg(img)
    draw_decorative_lines(draw)

    top1 = data[0]

    # 티저: 1위 종목명 (블러 처리 흉내 — 검은 박스)
    draw_text_centered(draw, "🏆  상승여력 1위 종목  🏆", 80, fonts["lg"], C_ACCENT)

    # 블러 박스 (힌트만 제공)
    bx1, by1 = MARGIN + 40, 170
    bx2, by2 = SIZE[0] - MARGIN - 40, 290
    draw_rounded_rect(draw, (bx1, by1, bx2, by2), 18, C_HEADER_BG, C_ACCENT)

    stock_hint = f"{'★' * len(top1['종목명'][:5])}  ({top1['종목코드'][:3]}***)"
    draw_text_centered(draw, stock_hint, by1 + 28, fonts["lg"], C_GREY)

    # 상승여력 수치 (공개)
    pct_text = f"상승여력  {top1['상승여력(%)']:+.2f}%"
    draw_text_centered(draw, pct_text, 320, fonts["xl"], C_UP)

    # 구분선
    draw.line([(MARGIN + 80, 415), (SIZE[0] - MARGIN - 80, 415)],
              fill=hex_to_rgb(C_DIVIDER), width=2)

    # CTA 박스
    cta_bx1, cta_by1 = MARGIN, 440
    cta_bx2, cta_by2 = SIZE[0] - MARGIN, 720
    draw_rounded_rect(draw, (cta_bx1, cta_by1, cta_bx2, cta_by2), 24, C_BG_CARD, C_ACCENT)

    cta_lines = [
        ("압도적 상승 여력의 1위 종목과",   fonts["md"], C_WHITE,   cta_by1 + 50),
        ("상세 통계 리포트를 보려면",        fonts["md"], C_WHITE,   cta_by1 + 100),
        ("👇  프로필 링크를 클릭하세요!  👇", fonts["md"], C_ACCENT,  cta_by1 + 160),
    ]
    for text, fnt, color, y in cta_lines:
        draw_text_centered(draw, text, y, fnt, color)

    # 링크 버튼 모양
    btn_x1 = SIZE[0] // 2 - 220
    btn_y1 = cta_by1 + 220
    btn_x2 = SIZE[0] // 2 + 220
    btn_y2 = btn_y1 + 64
    draw_rounded_rect(draw, (btn_x1, btn_y1, btn_x2, btn_y2), 32, C_ACCENT, None)
    draw_text_centered(draw, "📲  프로필 링크 바로가기",
                       btn_y1 + 14, fonts["sm"], "#1A237E")

    # 팔로우 유도
    draw_text_centered(draw, "매일 아침 TOP 10 리포트를 받아보세요 ✅",
                       755, fonts["sm"], C_GREY)
    draw_text_centered(draw, "#주식 #증권리포트 #목표주가 #상승여력 #오늘의주식",
                       810, fonts["xs"], C_DIVIDER)

    # 날짜
    draw_text_centered(draw, today_str, 870, fonts["xs"], C_GREY)

    draw.line([(MARGIN, SIZE[1] - 55), (SIZE[0] - MARGIN, SIZE[1] - 55)],
              fill=hex_to_rgb(C_DIVIDER), width=1)
    warn = "본 자료는 투자 참고용이며, 투자 판단의 책임은 본인에게 있습니다."
    draw_text_centered(draw, warn, SIZE[1] - 45, fonts["tiny"], C_GREY)

    draw_logo_badge(draw, fonts)
    return img


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    today_str = datetime.today().strftime("%Y-%m-%d")
    json_name = f"upside_{today_str.replace('-','')}.json"

    # JSON 로드
    if not Path(json_name).exists():
        print(f"❌ {json_name} 파일이 없습니다. target_price_analyzer.py 를 먼저 실행하세요.")
        sys.exit(1)

    with open(json_name, encoding="utf-8") as f:
        raw_data = json.load(f)

    # 상승여력 내림차순 정렬 → 상위 10개
    data = sorted(raw_data, key=lambda x: x["상승여력(%)"], reverse=True)[:10]
    print(f"📂 데이터 로드: {json_name} ({len(data)}종목)")

    if len(data) < 5:
        print("❌ 유효 데이터가 5개 미만입니다. 데이터를 확인해 주세요.")
        sys.exit(1)

    # 폰트 로드
    font_path = find_korean_font()
    print(f"🔤 한글 폰트: {font_path}")
    fonts = load_fonts(font_path)

    output_dir = Path(".")
    cards = [
        ("card_1.png", "표지",          lambda: make_card1(fonts, today_str)),
        ("card_2.png", "2~5위 본문",     lambda: make_card2(fonts, data, today_str)),
        ("card_3.png", "CTA (1위 공개)", lambda: make_card3(fonts, data, today_str)),
    ]

    print("\n🎨 카드뉴스 생성 중...\n")
    for filename, label, fn in cards:
        img = fn()
        out_path = output_dir / filename
        img.save(str(out_path), "PNG", quality=95)
        size_kb = out_path.stat().st_size // 1024
        print(f"  ✅ {filename}  ({label})  →  {size_kb} KB")

    print(f"\n🎉 완료! 3장 모두 {output_dir.resolve()} 에 저장되었습니다.")
    print("=" * 60)
    print(f"  1위: {data[0]['종목명']}  ({data[0]['종목코드']})")
    print(f"       상승여력  {data[0]['상승여력(%)']:+.2f}%  |  목표가 {data[0]['목표주가']:,}원")
    print("=" * 60)


if __name__ == "__main__":
    main()
