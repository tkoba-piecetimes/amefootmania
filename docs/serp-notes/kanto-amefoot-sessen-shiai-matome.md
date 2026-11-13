# SERP分析メモ: 関東学生アメフト 接戦の試合まとめ（K5系・企画）

- 作成日: 2026-11-13
- 類型: K（企画・公開データ集計）。KW在庫のPが全件消化済みのため、K5「名勝負10選」を「規定時間7点差以内の一覧」に再定義して採用（主観的な名勝負選定は避け、公式結果の得点差で機械的に抽出）
- 狙いKW: 関東学生アメフト 接戦 / 僅差 試合 / TOP8 1点差

## 確認した事実（一次情報）

- KCFA 順位順列決定方法（https://www.kcfa.jp/rankingmethod/）: 勝ち3点・引き分け1点・負け0点／順列6基準／TOP8-7位 vs BIG8-2位、TOP8-8位 vs BIG8-1位のチャレンジマッチ／同点はタイブレークで勝敗を決し、その得点は得失点差に含めない
- 各試合の公式結果PDF（https://www.kcfa.jp/files/user/result_pdf/）: 2026-10-18 明治14-14法政は延長1回3-3・延長2回0-8（合計3-11）、2026-11-01 立教15-15慶應は延長1回7-7・延長2回8-6（合計15-13）をPDFテキスト抽出で確認
- 集計は data/leagues/top8/history/2024.json・2025.json と matches.json（2026年11月13日時点で24試合消化）から。BIG8は形式が年度で異なるため件数のみ

## SERP所見（WebSearch「関東学生アメフト 接戦 僅差 名勝負 TOP8 1点差 逆転」）

1. 上位は spaia・早稲田大学競技スポーツセンター・Daily などの個別試合レポート。試合単位の記事が中心で、シーズン横断の接戦の一覧・割合・チーム別集計は見当たらない
2. 全日本大学選手権や甲子園ボウルなどポストシーズンの接戦記事が目立つ。関東リーグ戦（TOP8・BIG8）の接戦を点差で網羅した資料は検索結果になかった
3. 差別化点: 公式結果PDFにひも付いた全試合の一覧、年度別の接戦率、同点→タイブレーク5試合、チーム別の接戦の勝敗、観戦カードの探し方。サンプルが小さい点を明記し、「接戦に強い」などの断定はしない

## 内部リンク先（一次データ）

- site/top8/standings, schedule, records, clubs/<slug>, matches/<id>（2026年分）、site/big8/standings, schedule
- 関連記事: amefoot-tiebreak-rule-guide, kanto-amefoot-junihyo-guide, kanto-amefoot-tsusan-shoritsu-guide, kanto-amefoot-heikin-tokuten-shitten-ranking, top8-big8-guide, amefoot-stadium-guide, kanto-amefoot-nittei-konshumatsu-guide

## 備考

- 既存 amefoot-tiebreak-rule-guide は2023〜2025年度6試合の記述。2026年度のタイブレーク2試合（上記）は未反映のため、次回リライト時に追記候補
