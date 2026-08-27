# -*- coding: utf-8 -*-
"""チーム名 → URLスラッグの対応表とスラッグ解決ロジック（アメフト版）。

kcfa.jp の星取表は行の先頭セルに「○○大学」のフル表記を使う（見出し行は「○○大」
のような省略表記だが、フル表記の方をチーム名として採用している）。
解決順: 1) 手動登録の対応表  2) pykakasiによるローマ字化  3) ハッシュフォールバック
"""
import re
import sys

TEAM_SLUGS = {
    # ---- TOP8 ----
    "早稲田大学": "waseda",
    "法政大学": "hosei",
    "慶應義塾大学": "keio",
    "立教大学": "rikkyo",
    "東京大学": "tokyo-u",
    "明治大学": "meiji",
    "桜美林大学": "obirin",
    "中央大学": "chuo",
    "日本体育大学": "nittaidai",

    # ---- BIG8 ----
    "駒澤大学": "komazawa",
    "青山学院大学": "aoyamagakuin",
    "国士舘大学": "kokushikan",
    "横浜国立大学": "yokohama-kokuritsu",
    "帝京大学": "teikyo",
    "明治学院大学": "meijigakuin",
    "東海大学": "tokai",
    "日本大学": "nihon",
    "専修大学": "senshu",
    "一橋大学": "hitotsubashi",
}

_kks = None


def _romaji(name: str) -> str | None:
    global _kks
    try:
        if _kks is None:
            import pykakasi
            _kks = pykakasi.kakasi()
        base = re.sub(r"(大学院|大学|高校|高)$", "", name.strip())
        s = "".join(x["hepburn"] for x in _kks.convert(base))
        s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
        return s or None
    except Exception:
        return None


def slug_for(team: str) -> str:
    if team in TEAM_SLUGS:
        return TEAM_SLUGS[team]
    r = _romaji(team)
    if r:
        TEAM_SLUGS[team] = r
        return r
    print(f"[warn] スラッグ生成不可のチーム名: {team}", file=sys.stderr)
    return f"team-{abs(hash(team)) % 10**8}"
