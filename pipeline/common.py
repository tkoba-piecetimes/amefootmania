# -*- coding: utf-8 -*-
"""取得スクリプトで共有するヘルパー（rugbymania の pipeline/common.py を流用）。"""
import sys
import time
import urllib.error
import urllib.request
from datetime import date

UA = "Mozilla/5.0 (compatible; AmefootManiaBot/1.0)"


def fetch(url: str, retries: int = 3) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                return res.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt == retries - 1:
                raise
            print(f"[warn] fetch failed ({e}), retrying in {10 * (attempt + 1)}s...", file=sys.stderr)
            time.sleep(10 * (attempt + 1))


def match_date_iso(month: int, day: int, season_start_year: int) -> str | None:
    # KCFAのシーズンは8月末開幕〜12月（年をまたがない）。
    try:
        return date(season_start_year, month, day).isoformat()
    except ValueError:
        return None


def build_teams(matches: list[dict], slug_for) -> dict[str, dict]:
    teams = {}
    for m in matches:
        for team in (m["home"], m["away"]):
            teams.setdefault(team, {"team": team, "slug": slug_for(team),
                                    "block": m["category"]})
    return teams
