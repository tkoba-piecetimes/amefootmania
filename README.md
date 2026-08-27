# アメフトマニア — 大学アメフト情報メディア（社内用）

大学アメリカンフットボールの情報メディア「アメフトマニア」。
rugbymania（C:\Users\tatsu\claudecode\rugbymania）のアーキテクチャを移植した第2弾。

- 公開URL: https://tkoba-piecetimes.github.io/amefootmania/
  （カスタムドメインは未取得。取得後は pipeline/generate_site.py の SITE_BASE を変更する。
  **現在このURLは下記「暫定noindex」により検索エンジンに非公開**）
- 対象: **関東学生アメリカンフットボール連盟（KCFA・https://www.kcfa.jp/）のTOP8・BIG8のみ**
  （関西・2部以下・医科歯科・7人制は対象外。第2フェーズ候補）
- 直近シーズン＋過去3シーズン分のデータ、試合ページ、記録室

## 仕組み

```
kcfa.jp/result_team/?season=YYYY（星取表・過去〜現シーズンのスコア・順位）
kcfa.jp/result_date/（今シーズンの月別日程・現シーズンのみ有効）
  → pipeline/fetch_amefoot_kanto.py
    ※ pipeline/common.py に共通ロジック（fetch）
    ※ pipeline/team_slugs.py にチーム名→スラッグ対応表
  → data/leagues/<top8|big8>/
  → pipeline/generate_site.py
  → site/
```

## 実行

```
python pipeline/fetch_amefoot_kanto.py
python pipeline/generate_site.py
```

ローカル確認: `python -m http.server 8941 -d site`

## データソースの詳細（rugbymaniaとの相違点）

- 星取表（result_team）はリーグ区分ごとに `<section class="result_list" id="result_team_N">`
  ブロックがあり、区分名が「TOP8」「BIG8」を含むものだけ採用する。BIG8は年度によって
  単一ブロックの年（2024・2025）と、Aブロック/Bブロック→二次上位リーグ/二次チャレンジ
  リーグに分かれる年（2023・2026）があるため、パーサーは区分名の文字列一致のみで判定し、
  ブロック構造の違いを吸収している。
- 勝敗・勝ち点・順位（「順位」列）・最終順位（「順列」列、タイブレーク後の確定順位）は
  KCFAが算出済みの値をそのまま採用する（自前の順位計算はしない）。得失点差のみ、
  試合結果から編集部が集計した参考値。
- 同点でもタイブレークで決着するカードがある（例: 2025年度TOP8 立教大-東京大
  17-17、東京大がタイブレーク15-13で勝利）。星取表のセルは「21○0」のように
  自チーム得点/勝敗記号（○●、まれに◯表記ゆれあり）/相手チーム得点の形式で、
  勝敗記号の方が正なので、スコア比較ではなく記号から勝敗を判定している
  （fetch側でmatchesに`winner`フィールドとして書き出す）。
- 日付は試合結果PDFへのリンク（`result_pdf/YYYYMMDD##.pdf`）のファイル名から取得。
  会場・時間はresult_team側には無い。
- 当シーズンの「今後の試合」（日程・会場）は result_date/ から補完している
  （このページは season パラメータを無視して常に現シーズンを表示するため、
  過去シーズンには使えない）。二次リーグ（BIG8二次上位リーグ等）は一次リーグ終了前
  「Aブロック1位」等のプレースホルダー名で埋まっており、実チーム名に解決されるまで
  ブロックごとスキップする。

## サイト方針（rugbymaniaとの相違点）

- 外部サービス連携のCTA・協賛導線は一切設置しない。運営元情報はサイトのどこにも表示しない。
- GA4測定ID・Search Console確認トークンは未発行のため空欄
  （pipeline/generate_site.py の page() 内にgtag挿入コードをコメントアウトで用意済み。
  発行後はIDを設定してコメントを解除する）。
- /contact ページは今回未実装（6媒体共通のフォーム基盤を別トラックで実装中、後日追加）。
- フッターに出典明記（関東学生アメリカンフットボール連盟へのリンク）。

## 暫定noindex（カスタムドメイン取得までの措置・2026-08-27追加）

現在の配信URL（`tkoba-piecetimes.github.io/amefootmania`）はURL自体に運営元を示す
文字列を含むため、カスタムドメイン取得までの間、検索エンジンに拾われないよう
以下の2点を有効にしている。

- `pipeline/generate_site.py` の `TEMP_NOINDEX = True`（ファイル冒頭の定数）
  - `True` の間、生成される全ページの `<head>` に
    `<meta name="robots" content="noindex, nofollow">` を出力する
  - `True` の間、`site/robots.txt` を `User-agent: *` / `Disallow: /`（全面クロール拒否）にする
- 通常時（サイト稼働中の恒常仕様）は、noindexダッシュボード（`dash-am-ops`）以外の
  全ページがインデックス対象になり、robots.txtも `Allow: /` ＋ sitemap.xml案内になる

**解除手順**（カスタムドメイン設定後）:

1. `pipeline/generate_site.py` の `SITE_BASE` をカスタムドメインのURLに変更
2. 同ファイルの `TEMP_NOINDEX` を `False` に変更
3. `python pipeline/generate_site.py` を再実行
4. 変更を commit・push（push時に Actions が自動デプロイする）
5. 本番HTMLで `<meta name="robots">` タグが消えていること、`robots.txt` が
   `Allow: /` に戻っていることを確認する

## 画像クレジット（内部記録・2026-08-27追加、同日hero差し替え）

| ファイル | 用途 | 出典 | ライセンス／備考 |
| --- | --- | --- | --- |
| `assets/hero.jpg` | トップページ hero（`build_portal`） | 運営提供素材（2026-08-27、木場さん提供） | 提供元管理。架空チーム「VALOR」のAI生成ビジュアルで実在選手の肖像は含まない。元WebP（1672x941）をJPEG変換・幅1600pxに圧縮して配置 |
| `assets/ogp.png` | OGP/Twitterカード画像（全ページ共通、`page()`内で自動参照） | https://www.pexels.com/photo/a-football-helmet-on-a-field-at-night-28239821/ | Pexels License（商用利用可・帰属不要） |
| `assets/league-header.jpg` | リーグトップページ（TOP8・BIG8共通）のヘッダー画像（`build_league`） | https://www.pexels.com/photo/black-and-white-football-on-wooden-posts-32963711/ | Pexels License（商用利用可・帰属不要） |

Pexels由来の画像はいずれも元画像をトリミング・幅1600px程度にリサイズ・JPEG品質80（`ogp.png`のみPNG化）で圧縮。
Pexels Licenseの全文: https://www.pexels.com/license/ （商用利用可・帰属表示不要、選手の顔が大きく写るもの・
NFL等の商標が明確に写るものは選定除外という基準で採用可否を判断）。

旧hero（Pexels「American Football Ball」26707860）は2026-08-27にhero差し替えに伴い削除。他スロットでは
使用していない。

## 未実装（今後）

- カスタムドメイン取得・GitHub Pages設定
- GA4 / Search Console 連携
- /contact ページ（6媒体共通フォーム基盤の実装待ち）
- 関西学生アメリカンフットボール連盟（第2フェーズ）
