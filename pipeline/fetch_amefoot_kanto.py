# -*- coding: utf-8 -*-
"""関東学生アメリカンフットボール連盟（kcfa.jp）からTOP8・BIG8の日程・結果・順位を取得し、
data/leagues/<code>/ に正規化JSONとして保存する（当シーズン）。
過去シーズンは data/leagues/<code>/history/<year>.json に保存する。

データ出典: 関東学生アメリカンフットボール連盟 (https://www.kcfa.jp/)

kcfa.jp/result_team/?season=YYYY の「星取表」はリーグ区分ごとに
<section class="result_list" id="result_team_N"> ブロックがあり、区分名は
<div class="block_title"><img alt="TOP8|BIG8"></div> または <h3><span>…</span></h3>
（BIG8がAブロック/Bブロック/二次上位リーグ/二次チャレンジリーグに分割される年がある）
に入っている。区分名に「TOP8」「BIG8」を含むブロックだけを対象にする
（2部・3部・医科歯科・7人制は対象外）。

対戦表は <table class="scheduletable"> のラウンドロビン形式。各セルは
「21○0」（自チーム得点/勝敗記号/相手チーム得点）＋試合結果PDFへのリンクで、
勝敗・勝ち点・順位・順列（タイブレーク後の最終順位）は連盟側で算出済みの値を
そのまま採用する（自前の順位計算はしない）。日付は試合結果PDFのファイル名
（例: result_pdf/2025110902.pdf → 2025-11-09）から取得する。会場・時間はこの
ページには含まれないため空欄になる。

なお二次リーグ（BIG8二次上位リーグ等）は一次リーグ終了前は「Aブロック1位」等の
プレースホルダー名で行が埋まっており、実チーム名に解決されるまではブロックごと
スキップする。
"""
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

from common import fetch
from team_slugs import slug_for

BASE = "https://www.kcfa.jp"
CURRENT_SEASON = 2026
HISTORY_SEASONS = [2025, 2024, 2023]
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "leagues"

SOURCE_NAME = "関東学生アメリカンフットボール連盟"
SOURCE_URL = f"{BASE}/"

SECTION_RE = re.compile(
    r'<section class="result_list" id="result_team_\d+">(.*?)</section>', re.DOTALL)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
H3_RE = re.compile(r"<h3><span>([^<]*)</span></h3>")
BLOCK_IMG_RE = re.compile(r'<div class="block_title"><img[^>]*alt="([^"]*)"')
TABLE_RE = re.compile(r'<table class="scheduletable">(.*?)</table>', re.DOTALL)
TR_RE = re.compile(r"<tr>(.*?)</tr>", re.DOTALL)
CELL_RE = re.compile(r"<t[hd]>(.*?)</t[hd]>", re.DOTALL)
LINK_RE = re.compile(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SCORE_RE = re.compile(r"^(\d+)([○◯●△])(\d+)$")
PDF_DATE_RE = re.compile(r"result_pdf/(\d{4})(\d{2})(\d{2})\d*\.pdf")
PLACEHOLDER_RE = re.compile(r"^[A-Zａ-ｚA-Za-z]?ブロック?\d+位$")

WIN_SYMBOLS = {"○", "◯"}
LOSS_SYMBOLS = {"●"}
DRAW_SYMBOLS = {"△"}


def cell_text_href(raw: str) -> tuple[str, str | None]:
    raw = raw.strip()
    m = LINK_RE.search(raw)
    if m:
        return TAG_RE.sub("", m.group(2)).strip(), m.group(1)
    return TAG_RE.sub("", raw).strip(), None


def classify_league(label: str) -> tuple[str, str] | tuple[None, None]:
    if "TOP8" in label:
        return "top8", "TOP8"
    if "BIG8" in label:
        return "big8", "BIG8"
    return None, None


def pdf_date(href: str | None) -> str | None:
    if not href:
        return None
    m = PDF_DATE_RE.search(href)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
    except ValueError:
        return None


def parse_blocks(html: str) -> list[dict]:
    """1シーズン分のHTMLからTOP8・BIG8の各ブロック（区分）を抽出する。"""
    blocks = []
    for body in SECTION_RE.findall(html):
        clean = COMMENT_RE.sub("", body)
        h3 = H3_RE.search(clean)
        if h3:
            label = h3.group(1).strip()
        else:
            img = BLOCK_IMG_RE.search(clean)
            label = img.group(1).strip() if img else ""
        league_code, league_name = classify_league(label)
        if not league_code:
            continue
        table_m = TABLE_RE.search(clean)
        if not table_m:
            continue
        rows = TR_RE.findall(table_m.group(1))
        if len(rows) < 2:
            continue  # 空テーブル（区分見出しのみのブロック）

        header_cells = [cell_text_href(c)[0] for c in CELL_RE.findall(rows[0])]
        if len(header_cells) < 6:  # 空th + 最低1チーム + 勝敗/勝ち点/順位/順列
            continue
        n = len(header_cells) - 5
        header_teams = header_cells[1:1 + n]

        row_names, row_cells = [], []
        for r in rows[1:]:
            cells = [cell_text_href(c) for c in CELL_RE.findall(r)]
            if len(cells) != n + 5:
                continue
            row_names.append(cells[0][0])
            row_cells.append(cells)

        if not row_names or any(PLACEHOLDER_RE.match(nm) for nm in row_names):
            continue  # 二次リーグ未確定（プレースホルダーチーム名のまま）

        matches, standings_entries = [], []
        for i, cells in enumerate(row_cells):
            home_full = cells[0][0]
            summary = cells[1 + n:1 + n + 4]
            wl_text = summary[0][0].strip()
            pts_text = summary[1][0].strip()
            rank_text = summary[2][0].strip()
            order_text = summary[3][0].strip()
            if pts_text.isdigit():
                wins = losses = 0
                if re.fullmatch(r"\d+-\d+", wl_text):
                    wins, losses = (int(x) for x in wl_text.split("-"))
                standings_entries.append({
                    "team": home_full,
                    "slug": slug_for(home_full),
                    "points": int(pts_text),
                    "wins": wins,
                    "losses": losses,
                    "draws": 0,
                    "games": wins + losses,
                    "rank": int(rank_text) if rank_text.isdigit() else None,
                    "order": int(order_text) if order_text.isdigit() else None,
                    "gf": 0,
                    "ga": 0,
                })
            for j in range(i + 1, n):
                text, href = cells[1 + j]
                text = text.strip()
                if text in ("", "―", "-"):
                    continue
                m = SCORE_RE.match(text)
                if not m:
                    continue
                own_score, symbol, opp_score = m.groups()
                away_full = row_names[j]
                own_score, opp_score = int(own_score), int(opp_score)
                if symbol in WIN_SYMBOLS:
                    winner = "home"
                elif symbol in LOSS_SYMBOLS:
                    winner = "away"
                else:
                    winner = "draw"
                d_iso = pdf_date(href)
                home_slug, away_slug = slug_for(home_full), slug_for(away_full)
                matches.append({
                    "id": f"{d_iso or 'tbd'}-{home_slug}-vs-{away_slug}",
                    "date": d_iso,
                    "time": "未定",
                    "category": label,
                    "home": home_full,
                    "away": away_full,
                    "home_slug": home_slug,
                    "away_slug": away_slug,
                    "venue": "",
                    "status": "played",
                    "home_score": own_score,
                    "away_score": opp_score,
                    "winner": winner,
                    "pdf_url": href or "",
                    "note": "",
                })

        # 得失点（表示用の集計値。順位・勝ち点は連盟公表値をそのまま使うため
        # ここでは使わない）
        totals: dict[str, list[int]] = {nm: [0, 0] for nm in row_names}
        for m in matches:
            totals[m["home"]][0] += m["home_score"]
            totals[m["home"]][1] += m["away_score"]
            totals[m["away"]][0] += m["away_score"]
            totals[m["away"]][1] += m["home_score"]
        for e in standings_entries:
            gf, ga = totals.get(e["team"], [0, 0])
            e["gf"], e["ga"] = gf, ga
            diff = gf - ga
            e["goal_diff"] = f"+{diff}" if diff > 0 else str(diff)
        standings_entries.sort(
            key=lambda e: (e["order"] if e["order"] is not None
                           else (e["rank"] if e["rank"] is not None else 999)))

        teams = {nm: {"team": nm, "slug": slug_for(nm), "block": label} for nm in row_names}

        blocks.append({
            "league_code": league_code,
            "league_name": league_name,
            "block_label": label,
            "matches": matches,
            "standings_entries": standings_entries,
            "teams": teams,
            "abbrev_to_full": dict(zip(header_teams, row_names)),
        })
    return blocks


# ---- result_date/（月別日程）: 星取表にまだスコアが入っていない「今後の試合」を
# 日付・会場つきで補う。season パラメータは無視され常に現シーズンが表示されるため、
# 当シーズンの分だけこれで補完する（過去シーズンは星取表のみで完結する）。

MONTH_SECTION_RE = re.compile(
    r"<h3><span>(\d{1,2})月</span></h3>\s*<table class=\"scheduletable\">(.*?)</table>",
    re.DOTALL)
GAME_CELL_RE = re.compile(r'(.*?)<span class="score">([^<]*)</span>(.*)', re.DOTALL)


def parse_game_cell(raw: str) -> tuple[str, str] | None:
    m = GAME_CELL_RE.search(raw)
    if not m:
        return None
    team1 = TAG_RE.sub("", m.group(1)).strip()
    team2 = TAG_RE.sub("", m.group(3)).strip()
    if not team1 or not team2:
        return None
    return team1, team2


def parse_upcoming_schedule(html: str, abbrev_index: dict[str, tuple[str, str, str]],
                             season_year: int) -> list[dict]:
    """abbrev_index: 短縮チーム名 -> (フル名, league_code, block_label)"""
    matches = []
    seen_pairs = set()
    for mon_str, table_html in MONTH_SECTION_RE.findall(html):
        month = int(mon_str)
        for row in TR_RE.findall(table_html):
            cells = [cell_text_href(c)[0] for c in CELL_RE.findall(row)]
            if len(cells) < 4 or not re.fullmatch(r"\d{1,2}/\d{1,2}", cells[0].strip()):
                continue
            _, day = cells[0].strip().split("/")
            venue = cells[2].strip()
            raw_cells = CELL_RE.findall(row)
            for raw in raw_cells[3:]:
                parsed = parse_game_cell(raw)
                if not parsed:
                    continue
                abbr1, abbr2 = parsed
                if abbr1 not in abbrev_index or abbr2 not in abbrev_index:
                    continue  # TOP8/BIG8以外（2部・3部等）は対象外
                full1, code1, label1 = abbrev_index[abbr1]
                full2, code2, _ = abbrev_index[abbr2]
                if code1 != code2:
                    continue
                try:
                    d_iso = date(season_year, month, int(day)).isoformat()
                except ValueError:
                    continue
                pair_key = (d_iso, frozenset((full1, full2)))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                slug1, slug2 = slug_for(full1), slug_for(full2)
                matches.append({
                    "id": f"{d_iso}-{slug1}-vs-{slug2}",
                    "date": d_iso,
                    "time": "未定",
                    "category": label1,
                    "home": full1,
                    "away": full2,
                    "home_slug": slug1,
                    "away_slug": slug2,
                    "venue": venue,
                    "status": "scheduled",
                    "home_score": None,
                    "away_score": None,
                    "winner": None,
                    "pdf_url": "",
                    "note": "",
                    "_league_code": code1,
                })
    return matches


def fetch_season(season_year: int, with_upcoming: bool = False) -> dict[str, dict]:
    html = fetch(f"{BASE}/result_team/?season={season_year}")
    blocks = parse_blocks(html)
    result: dict[str, dict] = {}
    abbrev_index: dict[str, tuple[str, str, str]] = {}
    for b in blocks:
        code = b["league_code"]
        d = result.setdefault(code, {
            "league_name": b["league_name"], "matches": [], "standings": {}, "teams": {},
        })
        d["matches"].extend(b["matches"])
        if b["standings_entries"]:
            d["standings"][b["block_label"]] = b["standings_entries"]
        d["teams"].update(b["teams"])
        for abbr, full in b["abbrev_to_full"].items():
            abbrev_index[abbr] = (full, code, b["block_label"])

    if with_upcoming:
        try:
            date_html = fetch(f"{BASE}/result_date/")
        except Exception as e:
            print(f"result_date/ の取得に失敗（今後の試合は未掲載）: {e}", file=sys.stderr)
            date_html = ""
        if date_html:
            already_played_pairs = {
                frozenset((m["home"], m["away"]))
                for d in result.values() for m in d["matches"]
            }
            for m in parse_upcoming_schedule(date_html, abbrev_index, season_year):
                if frozenset((m["home"], m["away"])) in already_played_pairs:
                    continue  # 既に星取表で結果が出ている試合は二重掲載しない
                code = m.pop("_league_code")
                result[code]["matches"].append(m)
    return result


def main() -> None:
    try:
        current = fetch_season(CURRENT_SEASON, with_upcoming=True)
    except Exception as e:
        print(f"当シーズンの取得に失敗: {e}", file=sys.stderr)
        current = {}

    history_by_code: dict[str, list[tuple[int, dict]]] = {}
    for year in HISTORY_SEASONS:
        try:
            season = fetch_season(year)
        except Exception as e:
            print(f"{year}シーズンの取得に失敗: {e}", file=sys.stderr)
            continue
        for code, d in season.items():
            history_by_code.setdefault(code, []).append((year, d))

    all_codes = set(current) | set(history_by_code)
    ok = 0
    for code in sorted(all_codes):
        league_name = (current[code]["league_name"] if code in current
                       else history_by_code[code][0][1]["league_name"])
        d = current.get(code, {"matches": [], "standings": {}, "teams": {}})
        if not d["teams"] and code in history_by_code:
            # 当季チームがまだ確定していない場合、直近の過去シーズンのチーム一覧を
            # 採用してチームページの入り口を確保する（rugbymania と同じ方針）。
            d = dict(d)
            d["teams"] = dict(history_by_code[code][0][1]["teams"])
        out_dir = DATA_DIR / code
        out_dir.mkdir(parents=True, exist_ok=True)
        played = sum(1 for m in d["matches"] if m["status"] == "played")
        meta = {
            "code": code,
            "region": "関東",
            "league": league_name,
            "season_year": CURRENT_SEASON,
            "source": SOURCE_NAME,
            "source_url": f"{BASE}/result_team/?season={CURRENT_SEASON}",
            "source_updated_at": date.today().isoformat(),
            "fetched_at": datetime.now().isoformat(timespec="seconds"),
        }
        (out_dir / "matches.json").write_text(
            json.dumps(d["matches"], ensure_ascii=False, indent=1), encoding="utf-8")
        (out_dir / "standings.json").write_text(
            json.dumps(d["standings"], ensure_ascii=False, indent=1), encoding="utf-8")
        (out_dir / "teams.json").write_text(
            json.dumps(d["teams"], ensure_ascii=False, indent=1), encoding="utf-8")
        (out_dir / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{code}: {league_name} 当季試合{len(d['matches'])}件(結果{played}) チーム{len(d['teams'])}"
              + ("" if code in current else " [当季データなし・過去のみ]"))
        ok += 1

        hist_dir = out_dir / "history"
        for year, hd in history_by_code.get(code, []):
            hist_dir.mkdir(parents=True, exist_ok=True)
            hplayed = sum(1 for m in hd["matches"] if m["status"] == "played")
            out = {"year": year, "league": hd["league_name"],
                   "matches": hd["matches"], "standings": hd["standings"]}
            (hist_dir / f"{year}.json").write_text(
                json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"  {year}/{code}: 試合{len(hd['matches'])}件(結果{hplayed})")

    print(f"done: {ok} categories (TOP8/BIG8)")


if __name__ == "__main__":
    main()
