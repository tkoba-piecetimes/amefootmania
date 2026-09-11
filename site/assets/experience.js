'use strict';
(() => {
  const app=document.querySelector('.football-app');
  document.querySelectorAll('.global-nav a').forEach(a=>{if(new URL(a.href).pathname===location.pathname)a.setAttribute('aria-current','page');});
  if(!app)return;
  const root=new URL('../',location.href),mode=app.dataset.mode;
  const esc=s=>String(s??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const today=new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Tokyo'}).format(new Date());
  const count=document.getElementById('result-count');
  const status=m=>m.status==='played'?'played':m.date&&m.date<today?'awaiting':'upcoming';
  const match=m=>{const played=m.status==='played';const tie=played&&m.home_score===m.away_score&&['home','away'].includes(m.winner)?` / ${esc(m[m.winner])} タイブレーク勝利`:'';const url=m.url?new URL(m.url,root).href:m.pdf_url;return `<${url?'a':'div'} class="match-card"${url?` href="${esc(url)}"`:''}><span class="match-meta">${esc(m.date||'日程未定')} · ${esc(m.category)}</span><span class="match-teams"><span>${esc(m.home)}</span><strong>${played?`${m.home_score} – ${m.away_score}`:'VS'}</strong><span>${esc(m.away)}</span></span><span class="match-meta">${played?'試合終了':status(m)==='awaiting'?'結果反映待ち':'試合予定'}${tie}${m.venue?' / '+esc(m.venue):''}${!m.url&&url?' / 公式結果PDF':''}</span></${url?'a':'div'}>`;};
  fetch(new URL('assets/football-data.json',root)).then(r=>{if(!r.ok)throw Error();return r.json();}).then(data=>{
    if(mode==='myteam'){
      const select=document.getElementById('favorite'),out=document.getElementById('myteam-results');
      const names=[...new Set(data.teams.map(t=>t.team))].sort((a,b)=>a.localeCompare(b,'ja'));
      names.forEach(t=>select.add(new Option(t,t)));
      try{const saved=localStorage.getItem('amefootmania.myteam');if(names.includes(saved))select.value=saved;}catch{}
      function draw(save=false){const team=select.value;let stored=true;if(save)try{if(team)localStorage.setItem('amefootmania.myteam',team);else localStorage.removeItem('amefootmania.myteam');}catch{stored=false;}
        count.textContent=team?`${team}を表示しています。${stored?'':'ブラウザへの保存ができないため、この画面のみで選択を保持します。'}`:'大学を選んでください。';
        if(!team){out.innerHTML='';return;}
        const latest=Math.max(...data.matches.map(m=>m.year));const ms=data.matches.filter(m=>m.year===latest&&(m.home===team||m.away===team));
        const recent=ms.filter(m=>m.status==='played').sort((a,b)=>(b.date||'').localeCompare(a.date||'')).slice(0,3);
        const next=ms.filter(m=>status(m)==='upcoming').sort((a,b)=>(a.date||'9999').localeCompare(b.date||'9999')).slice(0,3);
        const pending=ms.filter(m=>status(m)==='awaiting');
        out.innerHTML=`<p>${data.teams.filter(t=>t.team===team).map(t=>`<a class="primary-link" href="${esc(new URL(t.url,root).href)}">${esc(t.label)}のチームページ →</a>`).join(' ')}</p><h2>次の試合</h2><div class="match-grid">${next.map(match).join('')||'<p>今後の確定日程は未掲載です。</p>'}</div><h2>直近の結果</h2><div class="match-grid">${recent.map(match).join('')||'<p>掲載結果はありません。</p>'}</div>${pending.length?`<h2>結果反映待ち</h2><div class="match-grid">${pending.map(match).join('')}</div>`:''}<p><a href="../archive/index.html?team=${encodeURIComponent(team)}&year=all">この大学の過去の記録 →</a></p>`;
      }
      select.addEventListener('change',()=>draw(true));document.getElementById('clear-favorite').addEventListener('click',()=>{select.value='';draw(true);});draw();return;
    }
    const controls=[...app.querySelectorAll('select')],params=new URLSearchParams(location.search);let limit=30;
    controls.forEach(c=>{if([...c.options].some(o=>o.value===params.get(c.id)))c.value=params.get(c.id);});
    const val=id=>document.getElementById(id)?.value||'all',results=document.getElementById('match-results'),tables=document.getElementById('standings-results'),more=document.getElementById('load-more');
    function render(){const year=mode==='archive'?val('year'):app.dataset.season,league=val('league'),team=val('team');
      let ms=data.matches.filter(m=>(year==='all'||String(m.year)===year)&&(league==='all'||m.league===league)&&(team==='all'||m.home===team||m.away===team)&&(mode==='archive'?m.status==='played':val('status')==='all'||status(m)===val('status')));
      ms.sort((a,b)=>{if(mode==='matches'&&a.status!==b.status)return a.status==='played'?1:-1;return a.status==='played'?(b.date||'').localeCompare(a.date||''):(a.date||'9999').localeCompare(b.date||'9999');});
      count.textContent=`${ms.length}試合${ms.length>limit?`（${limit}試合を表示）`:''}`;
      results.innerHTML='<h2>試合'+(mode==='archive'?'結果':'一覧')+'</h2><div class="match-grid">'+(ms.slice(0,limit).map(match).join('')||'<p class="empty-result">条件に一致する試合はありません。年度・大学・リーグを変更してください。</p>')+'</div>';
      more.hidden=ms.length<=limit;
      if(mode==='archive'){
        const blocks=data.standings.filter(b=>(year==='all'||String(b.year)===year)&&(league==='all'||b.league===league)&&(team==='all'||b.entries.some(t=>t.team===team))).sort((a,b)=>b.year-a.year);
        tables.innerHTML='<h2>順位表</h2>'+(blocks.map(b=>`<section class="archive-block"><h3>${b.year}年 · ${esc(b.block)}</h3><div class="tbl" tabindex="0" role="region" aria-label="${b.year}年 ${esc(b.block)}の順位表"><table><thead><tr><th scope="col">順位</th><th scope="col">大学</th><th scope="col">勝ち点</th><th scope="col">試合</th><th scope="col">勝–敗</th><th scope="col">得失点差（参考）</th></tr></thead><tbody>${b.entries.map(t=>`<tr${t.team===team?' class="selected-team"':''}><td>${esc(t.rank)}</td><th scope="row">${esc(t.team)}${t.team===team?'（選択中）':''}</th><td>${esc(t.points)}</td><td>${esc(t.games)}</td><td>${esc(t.wins)}–${esc(t.losses)}</td><td>${esc(t.goal_diff)}</td></tr>`).join('')}</tbody></table></div><p class="note"><a href="${esc(b.source)}">${b.year}年の公式星取表（KCFA） ↗</a></p></section>`).join('')||'<p>条件に一致する順位表はありません。</p>');
      }
    }
    function sync(){const p=new URLSearchParams();controls.forEach(c=>p.set(c.id,c.value));history.replaceState(null,'','?'+p.toString());limit=30;render();}
    controls.forEach(c=>c.addEventListener('change',sync));more.addEventListener('click',()=>{limit+=30;render();});document.getElementById('reset').addEventListener('click',()=>{controls.forEach(c=>c.selectedIndex=0);sync();});render();
  }).catch(()=>{count.textContent='データを読み込めませんでした。ページを再読み込みするか、リーグ別ページをご利用ください。';});
})();
