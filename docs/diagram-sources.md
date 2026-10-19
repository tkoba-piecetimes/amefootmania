# 図解SVGの確認元（assets/diagrams/）

仕様: `.claude/skills/bukatsu-seo-article/reader-level-spec.md` §3。図ごとに、ルール・寸法・人数・位置関係を確認した公式情報を1行で記録する。
確認日: 2026-10-19。「規則書」= 日本アメリカンフットボール協会（JAFA）公式規則書 2026〜27年度版
`https://americanfootball.jp/wp-content/uploads/%E3%82%A2%E3%83%A1%E3%83%95%E3%83%88%E5%85%AC%E5%BC%8F%E3%83%AB%E3%83%BC%E3%83%AB%E3%83%96%E3%83%83%E3%82%AF2026-2027_%E8%BB%BD%E9%87%8F.pdf`

| slug | 描いている内容 | 確認元 |
| --- | --- | --- |
| amefoot-field-lines | ゴールライン間100ヤード・エンドゾーン各10ヤード（全長360フィート）・幅160フィート（48.77m）・ヤードラインは5ヤードごと・ハッシュマークはサイドラインから60フィート（18.29m） | 規則書 第1篇 第2章 第1条（フィールド）・第2篇 第12章（ライン）・付録D フィールド図 |
| amefoot-four-downs | 4回のダウンで10ヤード進めば新しいシリーズ、進めなければ相手のボール（攻守交代） | JAFA「はじめてのアメリカンフットボール」 https://americanfootball.jp/beginner/ ／規則書 第5篇（シリーズ）。第4ダウンのキック選択は図では扱わない |
| amefoot-scrimmage-neutral-zone | スクリメージライン＝ボール先端を通る線／ニュートラルゾーン＝2本の線の間でボールの長軸の長さ／スナップ時にディフェンスがニュートラルゾーン内か越えているとオフサイド | 規則書 第2篇 第16章（ニュートラルゾーン）・第18章 第2条（オフサイド） |
| amefoot-offense-positions | 1チーム11人以下。バックは4人まで（残り7人以上がライン上）。オフェンスラインはC・G・T、QB・RB・WR・TEの役割。並びは一例 | 規則書 第7篇 第1章 第4条（フォーメーション: バックは5人以上いてはならない）／ポジションの役割: https://second-effort.com/positions/offense/ ／ https://spaia.jp/column/american_football/1883 |
| amefoot-defense-positions | 4-3の一例。DL4・LB3・DB4（CB2・S2）の11人。DLがスクリメージライン沿い、LBがその後ろ、DBが後方と外側 | 11人: JAFA beginner ／4-3の構成: https://amefoot-club.com/football-classroom-defense-4-3-defensvie-front/ ／ DBの役割: https://spaia.jp/column/american_football/1883 ／ CB: https://ja.wikipedia.org/wiki/コーナーバック（公式規則書にポジション名の定義は無いため、一般的な解説で確認。図に「一例」と明記） |
| amefoot-scoring | タッチダウン6点・フィールドゴール3点・セイフティ2点・トライ（タッチダウン2点／フィールドゴールまたはセイフティ1点） | 規則書 第8篇 第1条（得点）／JAFA beginner（キック＝1点、ラン・パス＝2点の説明） |
| amefoot-tiebreak-start | 同点時のタイブレイクシステム。相手の25ヤードラインから、表（先攻）・裏（後攻）のポゼッションシリーズ。得点するか新たな第1ダウンの獲得に失敗するまで攻撃 | 規則書 第3篇 第1章 第3条（超過節）／KCFA 順位順列決定方法 https://www.kcfa.jp/rankingmethod/ ／ 2025-08-30 立教大-東京大 公式結果PDF（25ヤード起点の記録） |
| amefoot-kickoff-lines | キックオフ時のキックチームの制限線は自陣35ヤード、レシーブチームの制限線はその10ヤード前方。タッチされずゴールライン上か後方に当たったフリーキックはデッドでタッチバック、レシーブチームの25ヤードから | 規則書 第6篇 第1章 第1条（制限線）・第7条（フリーキックのタッチバック）。図では人数・並びの細則は描かない |
| amefoot-league-challenge | チャレンジマッチ＝TOP8の7位対BIG8の2位、TOP8の8位対BIG8の1位。同点ならタイブレイクシステムの超過節 | KCFA 順位順列決定方法 https://www.kcfa.jp/rankingmethod/ 。昇降格の扱い（負けた側の翌年の所属）は同ページに明記が無いため図には書いていない |

## 描かなかった図

- ルートツリー（WRのルート図）: 公式の定義が無く、チームごとに呼び名・本数が違うため見送り。
- 4-3以外の守備隊形（3-4・ニッケル等）: 初心者向けの優先度が低く、公式情報での確認が難しいため見送り。
- 各反則の位置関係図: 反則の細則が多く、記事の表で足りるため見送り。

## 注意

- 図は「一例」と明記したもの（offense-positions・defense-positions）以外も、実際の並び方・動きはチームや作戦で変わる。
- 辞典（data/glossary.json）の `diagram` は上記slugのみを参照する。
