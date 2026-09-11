from html import escape as e
from datetime import date
import json


def card(lg, m, prefix=''):
    played=m['status']=='played'
    score=f"{m['home_score']} – {m['away_score']}" if played else 'VS'
    status='試合終了' if played else ('結果反映待ち' if m.get('date') and m['date']<date.today().isoformat() else '試合予定')
    tie=f" / {m[m['winner']]} タイブレーク勝利" if played and m['home_score']==m['away_score'] and m.get('winner') in ('home','away') else ''
    return f'''<a class="match-card" href="{prefix}{lg['code']}/matches/{m['id']}/index.html"><span class="match-meta">{e(m.get('date') or '日程未定')} · {e(m['category'])}</span><span class="match-teams"><span>{e(m['home'])}</span><strong>{score}</strong><span>{e(m['away'])}</span></span><span class="match-meta">{status}{e(tie)}{(' / '+e(m['venue'])) if m.get('venue') else ''}</span></a>'''


def build(g, leagues, articles, meta):
    current=[(lg,m) for lg in leagues for m in lg['matches']]
    recent=sorted([(lg,m) for lg,m in current if m['status']=='played'],key=lambda x:x[1].get('date') or '',reverse=True)
    upcoming=sorted([(lg,m) for lg,m in current if m['status']=='scheduled' and m.get('date') and m['date']>=date.today().isoformat()],key=lambda x:x[1]['date'])
    team_count=len({t for lg in leagues for t in lg['teams']})
    league_cards=''.join(f'''<a class="league-card" href="{lg['code']}/index.html"><span>KANTO COLLEGE FOOTBALL</span><h3>{e(lg['label'])}</h3><p>{len(lg['teams'])}チーム · {lg['meta']['season_year']} SEASON</p><b>日程・順位・チームを見る ↗</b></a>''' for lg in leagues)
    body=f'''<div class="season-strip">COLLEGE FOOTBALL {meta['season_year']}<span>関東学生 TOP8・BIG8</span></div>
    <section class="editorial-hero"><img src="assets/hero.jpg" width="1600" height="900" alt="アメリカンフットボールのイメージ"><div class="hero-copy"><p class="eyebrow">EVERY DOWN. EVERY GAME.</p><h1>一球に、<br>すべてを。</h1><p>仲間の勝利も、ライバルの一戦も。<br>大学アメフトの熱を、ここから。</p><div class="hero-actions"><a class="primary-link" href="matches/index.html">試合結果をチェック →</a><a href="myteam/index.html">マイチームを選ぶ →</a></div><div class="hero-stats"><span><b>{len(leagues)}</b> カテゴリ</span><span><b>{team_count}</b> チーム</span><span><b>{meta['season_year']}</b> SEASON</span></div></div></section>
    <section><div class="section-heading"><div><p class="eyebrow">01 / MATCH CENTER</p><h2>試合の熱を、追いかけよう。</h2></div><a href="matches/index.html">全日程・結果 →</a></div><h3>最新の掲載結果</h3><div class="match-grid">{''.join(card(lg,m) for lg,m in recent[:4]) or '<p>掲載結果はまだありません。</p>'}</div><h3>次のキックオフ</h3><div class="match-grid">{''.join(card(lg,m) for lg,m in upcoming[:2]) or '<p>今後の確定日程は未掲載です。</p>'}</div><p class="note">情報更新：{e(meta['fetched_at'][:10])}。連盟公表データを掲載しています。ライブ速報ではありません。</p></section>
    <section id="leagues"><div class="section-heading"><div><p class="eyebrow">02 / THE LEAGUES</p><h2>あなたのリーグは、ここに。</h2></div></div><div class="league-grid">{league_cards}</div><p class="note">掲載対象は関東学生TOP8・BIG8です。ブロック名・年度は各表で確認できます。</p></section>
    <section class="database-promo"><p class="eyebrow">03 / FOOTBALL DATABASE</p><h2>あの対戦を、もう一度。</h2><p>年度・リーグ・大学から試合結果と順位表を探す。</p><a class="primary-link" href="archive/index.html">過去の記録を調べる →</a></section>
    <section><div class="section-heading"><div><p class="eyebrow">04 / JOURNAL</p><h2>アメフトを、もっと深く。</h2></div><a href="articles/index.html">読みもの一覧 →</a></div><div class="digest">{''.join(g.article_card(a,'') for a in articles[:3])}</div><p><a href="articles/american-football-watching-guide/index.html">はじめての観戦ガイド →</a></p></section>'''
    g.write_page('',g.page('',f'{g.SITE_NAME} | 大学アメフトの試合結果・順位・データ',body,meta))
    options=''.join(f'<option value="{lg["code"]}">{e(lg["label"])}</option>' for lg in leagues)
    teams=sorted({t for lg in leagues for _,ms in lg['matches_by_year'] for m in ms for t in (m['home'],m['away'])})
    team_options=''.join(f'<option>{e(t)}</option>' for t in teams)
    years=sorted({y for lg in leagues for y,_ in lg['matches_by_year']},reverse=True)
    dataset={'matches':[],'standings':[],'teams':[]}
    for lg in leagues:
        for year,ms in lg['matches_by_year']:
            for m in ms:
                dataset['matches'].append(dict(m,year=year,league=lg['code'],league_label=lg['label'],url=f"{lg['code']}/matches/{m['id']}/index.html" if year==lg['meta']['season_year'] else None))
        for year,standings in [(lg['meta']['season_year'],lg['standings'])]+[(h['year'],h['standings']) for h in lg['hist']]:
            for block,entries in standings.items():
                dataset['standings'].append({'year':year,'league':lg['code'],'block':block,'entries':entries,'source':f'https://www.kcfa.jp/result_team/?season={year}'})
        for t,info in lg['teams'].items():
            dataset['teams'].append({'team':t,'league':lg['code'],'label':lg['label'],'url':f"{lg['code']}/clubs/{info['slug']}/index.html"})
    (g.SITE/'assets'/'football-data.json').write_text(json.dumps(dataset,ensure_ascii=False),encoding='utf-8')
    for archive in [False,True]:
        slug='archive' if archive else 'matches'
        title='データベース' if archive else '試合・結果'
        year_options=''.join(f'<option value="{y}">{y}年</option>' for y in years)
        filters=(f'<label>年度<select id="year">{year_options}<option value="all">すべての年度</option></select></label>' if archive else '')
        filters+=f'<label>リーグ<select id="league"><option value="all">すべてのリーグ</option>{options}</select></label><label>大学<select id="team"><option value="all">すべての大学</option>{team_options}</select></label>'
        if not archive: filters+='<label>表示<select id="status"><option value="all">すべて</option><option value="upcoming">今後の試合</option><option value="played">試合結果</option><option value="awaiting">結果反映待ち</option></select></label>'
        fallback=''.join(f'<li><a href="../{lg["code"]}/{"records" if archive else "schedule"}/index.html">{lg["label"]}の{"記録室" if archive else "日程・結果"}</a></li>' for lg in leagues)
        body=f'''<p class="eyebrow">{'FOOTBALL DATABASE' if archive else 'MATCH CENTER'}</p><h1>{title}</h1><p>{'過去の試合結果と順位表を、このページで。' if archive else '関東学生TOP8・BIG8の試合を探す。'}</p><div class="football-app" data-mode="{slug}" data-season="{meta['season_year']}"><div class="filters">{filters}<button id="reset" type="button">条件をリセット</button></div><p id="result-count" role="status">データを読み込んでいます…</p><div id="standings-results"></div><div id="match-results"></div><button id="load-more" type="button" hidden>さらに30試合を表示</button></div><p class="note">更新：{e(meta['fetched_at'][:10])}。順位・勝ち点は連盟公表値、得失点差は試合結果からの参考集計です。同点スコアの決着は勝敗情報で表示します。</p><details><summary>リーグ別ページで見る</summary><ul>{fallback}</ul></details>'''
        g.write_page(slug,g.page('../',title+' | '+g.SITE_NAME,body,meta,path=slug+'/'))
    body='''<p class="eyebrow">MY TEAM</p><h1>いつも追いかける、あのチーム。</h1><p>大学を選ぶと、直近の結果と次の試合がすぐに見られます。選択はこのブラウザに保存されます。</p><div class="football-app" data-mode="myteam"><label>応援する大学<select id="favorite"><option value="">大学を選択</option></select></label><button id="clear-favorite" type="button">選択を解除</button><p id="result-count" role="status"></p><div id="myteam-results"></div></div>'''
    g.write_page('myteam',g.page('../','マイチーム | '+g.SITE_NAME,body,meta,path='myteam/'))
