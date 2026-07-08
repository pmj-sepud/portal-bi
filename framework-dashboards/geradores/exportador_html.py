"""
exportador_html.py — Camada de RENDERIZAÇÃO.

Recebe o pacote processado + a configuração e devolve uma página HTML única,
autossuficiente (sem dependências externas / CDNs). O mesmo template atende
tanto a dashboards de eventos quanto de ranking mensal; o modo é escolhido pela
config. Toda a lógica de KPIs, gráficos e filtros roda no navegador a partir dos
dados embutidos — exatamente o padrão dos dashboards Waze originais.
"""

import json


def exportar(pacote: dict, config: dict) -> str:
    cor = config.get("cor", {})
    payload = {
        "modo": pacote["tipo"],
        "titulo": config["titulo"],
        "subtitulo": config["subtitulo"],
        "cor": {
            "primaria": cor.get("primaria", "#1a5b9c"),
            "escura": cor.get("escura", "#0b2545"),
            "clara": cor.get("clara", "#4a90d9"),
            "accent": cor.get("accent", "#f5a623"),
        },
        "kpis": pacote["kpis"],
        "ruas": pacote["ruas"],
        "filtros": config.get("filtros", []),
        "graficos_cfg": config.get("graficos", {}),
    }

    if pacote["tipo"] == "eventos":
        payload.update({
            "registros": pacote["registros"],
            "serie_mes_ano": pacote["serie_mes_ano"],
            "anos": pacote["anos"],
            "ranking_ruas": pacote["ranking_ruas"],
            "periodo_counts": pacote["periodo_counts"],
            "periodos_label": pacote["periodos_label"],
            "tem_hora": pacote["tem_hora"],
        })
    else:  # ranking_mensal
        payload.update({
            "dados_ranking": pacote["dados_ranking"],
            "chaves_mes": pacote["chaves_mes"],
            "periodos_ranking": pacote["periodos_ranking"],
        })

    dados_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return _TEMPLATE.replace("/*__DADOS__*/", dados_json)


# ===========================================================================
# TEMPLATE HTML ÚNICO (institucional, self-contained)
# ===========================================================================
_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Dashboard — Portal de BI Joinville</title>
<style>
  :root{
    --pri:#1a5b9c; --esc:#0b2545; --cla:#4a90d9; --acc:#f5a623;
    --bg:#eef2f7; --card:#ffffff; --line:#dbe3ee;
    --ink:#1f2937; --ink2:#5a6b81; --ink3:#8493a6;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--ink)}
  .db-head{background:linear-gradient(135deg,var(--esc),var(--pri));color:#fff;padding:1.1rem 1.6rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap}
  .db-head h1{margin:0;font-size:1.2rem;font-weight:700}
  .db-head p{margin:.15rem 0 0;font-size:.8rem;opacity:.8}
  .db-badge{font-size:.78rem;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:.3rem .8rem;font-variant-numeric:tabular-nums}
  .db-filtros{background:var(--card);border-bottom:1px solid var(--line);padding:.8rem 1.6rem;display:flex;gap:.9rem;flex-wrap:wrap;align-items:flex-end}
  .fg{display:flex;flex-direction:column;gap:.25rem}
  .fg label{font-size:.62rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink3)}
  .fg select{border:1.5px solid var(--line);border-radius:8px;padding:.4rem .6rem;font-size:.85rem;background:#fff;color:var(--ink);min-width:120px;cursor:pointer}
  .fg select:focus{outline:none;border-color:var(--pri);box-shadow:0 0 0 3px rgba(26,91,156,.12)}
  .btn-limpar{border:1.5px solid var(--line);background:#fff;border-radius:8px;padding:.42rem .8rem;font-size:.8rem;cursor:pointer;color:var(--ink2)}
  .btn-limpar:hover{border-color:var(--pri);color:var(--pri)}
  .wrap{max-width:1280px;margin:0 auto;padding:1.4rem 1.6rem 3rem}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;margin-bottom:1.4rem}
  .kpi{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--pri);border-radius:12px;padding:1rem 1.1rem}
  .kpi .v{font-size:1.7rem;font-weight:800;color:var(--esc);font-variant-numeric:tabular-nums;line-height:1.1}
  .kpi .l{font-size:.76rem;color:var(--ink2);margin-top:.15rem}
  .kpi .ic{font-size:1rem;opacity:.8}
  .grid{display:grid;grid-template-columns:2fr 1fr;gap:1.2rem}
  @media(max-width:820px){.grid{grid-template-columns:1fr}}
  .panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:1.1rem 1.2rem;margin-bottom:1.2rem}
  .panel h2{margin:0 0 .1rem;font-size:1rem;color:var(--esc)}
  .panel .sub{margin:0 0 .8rem;font-size:.78rem;color:var(--ink3)}
  canvas{display:block;width:100%;max-width:100%}
  .rank-row{display:grid;grid-template-columns:1.4rem 1fr auto;gap:.5rem;align-items:center;padding:.28rem 0;font-size:.83rem}
  .rank-row .pos{color:var(--ink3);font-variant-numeric:tabular-nums;text-align:right;font-weight:700}
  .rank-bar{height:8px;border-radius:4px;background:var(--pri);opacity:.85}
  .rank-val{font-variant-numeric:tabular-nums;color:var(--ink2);font-size:.78rem;white-space:nowrap}
  .rank-name{font-size:.8rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .rank-wrap .rank-cell{display:flex;flex-direction:column;gap:2px;min-width:0}
  .empty{color:var(--ink3);font-size:.85rem;padding:1rem 0}
  .db-foot{max-width:1280px;margin:0 auto;padding:1.2rem 1.6rem;color:var(--ink3);font-size:.75rem;border-top:1px solid var(--line)}
</style>
</head>
<body>
  <div class="db-head">
    <div>
      <h1 id="db-titulo"></h1>
      <p id="db-subtitulo"></p>
    </div>
    <div class="db-badge" id="db-badge"></div>
  </div>
  <div class="db-filtros" id="db-filtros"></div>
  <div class="wrap">
    <div class="kpis" id="db-kpis"></div>
    <div id="db-corpo"></div>
  </div>
  <div class="db-foot">Gerado pelo Framework de Dashboards · Portal de BI · Prefeitura de Joinville · dados 1:1 com a planilha de origem.</div>

<script>
const P = /*__DADOS__*/;
document.documentElement.style.setProperty('--pri', P.cor.primaria);
document.documentElement.style.setProperty('--esc', P.cor.escura);
document.documentElement.style.setProperty('--cla', P.cor.clara);
document.documentElement.style.setProperty('--acc', P.cor.accent);
document.getElementById('db-titulo').textContent = P.titulo;
document.getElementById('db-subtitulo').textContent = P.subtitulo;

const MESES_ABR = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
const fmt = n => (typeof n==='number') ? n.toLocaleString('pt-BR') : n;

// ---------- helpers de gráfico (canvas puro) ----------
function setupCanvas(cv, h){
  const dpr = window.devicePixelRatio||1;
  const w = cv.clientWidth || cv.parentNode.clientWidth-20;
  cv.width = w*dpr; cv.height = h*dpr; cv.style.height = h+'px';
  const ctx = cv.getContext('2d'); ctx.scale(dpr,dpr);
  return {ctx,w,h};
}
function barChart(cv, labels, values){
  const {ctx,w,h} = setupCanvas(cv, 300);
  ctx.clearRect(0,0,w,h);
  const pad={l:44,r:12,t:14,b:34};
  const max = Math.max(1,...values);
  const bw = (w-pad.l-pad.r)/values.length;
  ctx.fillStyle='#8493a6'; ctx.font='10px system-ui'; ctx.textAlign='right';
  for(let g=0; g<=4; g++){
    const yv = max*g/4, y = h-pad.b-(h-pad.t-pad.b)*g/4;
    ctx.strokeStyle='#eef2f7'; ctx.beginPath(); ctx.moveTo(pad.l,y); ctx.lineTo(w-pad.r,y); ctx.stroke();
    ctx.fillText(Math.round(yv).toLocaleString('pt-BR'), pad.l-6, y+3);
  }
  const pri = getComputedStyle(document.documentElement).getPropertyValue('--pri').trim();
  for(let i=0;i<values.length;i++){
    const bh = (h-pad.t-pad.b)*values[i]/max;
    const x = pad.l+bw*i+bw*0.15, y=h-pad.b-bh;
    ctx.fillStyle=pri; ctx.globalAlpha=.88;
    ctx.fillRect(x,y,bw*0.7,bh); ctx.globalAlpha=1;
    ctx.fillStyle='#8493a6'; ctx.font='10px system-ui'; ctx.textAlign='center';
    ctx.fillText(labels[i], pad.l+bw*i+bw/2, h-pad.b+14);
  }
}
function donut(cv, labels, values){
  const {ctx,w,h} = setupCanvas(cv, 220);
  ctx.clearRect(0,0,w,h);
  const total = values.reduce((a,b)=>a+b,0)||1;
  const cx=110, cy=h/2, r=72, ir=44;
  const cols=['#0b2545','#1a5b9c','#4a90d9','#9cc4ee'];
  let ang=-Math.PI/2;
  for(let i=0;i<values.length;i++){
    const a2=ang+2*Math.PI*values[i]/total;
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.arc(cx,cy,r,ang,a2); ctx.closePath();
    ctx.fillStyle=cols[i%cols.length]; ctx.fill(); ang=a2;
  }
  ctx.globalCompositeOperation='destination-out';
  ctx.beginPath(); ctx.arc(cx,cy,ir,0,2*Math.PI); ctx.fill();
  ctx.globalCompositeOperation='source-over';
  ctx.fillStyle='#1f2937'; ctx.textAlign='center'; ctx.font='700 15px system-ui';
  ctx.fillText(fmt(total), cx, cy+5);
  // legenda
  let ly=24;
  for(let i=0;i<labels.length;i++){
    ctx.fillStyle=cols[i%cols.length]; ctx.fillRect(200,ly-8,10,10);
    ctx.fillStyle='#1f2937'; ctx.textAlign='left'; ctx.font='11px system-ui';
    const pct = ((values[i]/total)*100).toFixed(1);
    ctx.fillText(labels[i]+'  '+fmt(values[i])+' ('+pct+'%)', 216, ly);
    ly+=22;
  }
}
function scatter(cv, pts){
  const {ctx,w,h} = setupCanvas(cv, 300);
  ctx.clearRect(0,0,w,h);
  const lats=pts.map(p=>p[0]), lngs=pts.map(p=>p[1]);
  if(!pts.length){ctx.fillStyle='#8493a6';ctx.font='12px system-ui';ctx.fillText('Sem coordenadas',12,20);return;}
  const laMin=Math.min(...lats),laMax=Math.max(...lats),lnMin=Math.min(...lngs),lnMax=Math.max(...lngs);
  const pad=14;
  const pri = getComputedStyle(document.documentElement).getPropertyValue('--pri').trim();
  ctx.fillStyle=pri;
  for(const p of pts){
    const x=pad+(w-2*pad)*(p[1]-lnMin)/((lnMax-lnMin)||1);
    const y=pad+(h-2*pad)*(1-(p[0]-laMin)/((laMax-laMin)||1));
    ctx.globalAlpha=.35; ctx.beginPath(); ctx.arc(x,y,2.2,0,6.28); ctx.fill();
  }
  ctx.globalAlpha=1;
}
function rankingList(el, itens, maxv){
  el.innerHTML='';
  if(!itens.length){el.innerHTML='<div class="empty">Sem dados para o filtro atual.</div>';return;}
  const mx = maxv||Math.max(1,...itens.map(i=>i[1]));
  itens.forEach((it,idx)=>{
    const row=document.createElement('div'); row.className='rank-row';
    row.innerHTML='<div class="pos">'+(idx+1)+'</div>'+
      '<div class="rank-cell"><div class="rank-name" title="'+it[0]+'">'+it[0]+'</div>'+
      '<div class="rank-bar" style="width:'+(100*it[1]/mx)+'%"></div></div>'+
      '<div class="rank-val">'+fmt(it[1])+'</div>';
    el.appendChild(row);
  });
}

// ---------- render KPIs ----------
function renderKPIs(){
  const box=document.getElementById('db-kpis'); box.innerHTML='';
  P.kpis.forEach(k=>{
    let v=k.valor;
    if(k.formato==='int' && typeof v==='number') v=fmt(v);
    const d=document.createElement('div'); d.className='kpi';
    d.innerHTML=(k.icone?'<div class="ic">'+k.icone+'</div>':'')+
      '<div class="v">'+v+(k.sufixo||'')+'</div><div class="l">'+k.label+'</div>';
    box.appendChild(d);
  });
}

/* ============================ MODO: EVENTOS ============================ */
function initEventos(){
  document.getElementById('db-corpo').innerHTML =
    '<div class="grid">'+
      '<div class="panel"><h2>Ocorrências por mês</h2><p class="sub">Distribuição mensal no período selecionado</p><canvas id="c-mes"></canvas></div>'+
      '<div class="panel"><h2>Ranking de vias</h2><p class="sub">Top vias por volume de registros</p><div class="rank-wrap" id="c-rank"></div></div>'+
    '</div>'+
    '<div class="grid">'+
      (P.tem_hora?'<div class="panel"><h2>Por período do dia</h2><p class="sub">Faixa horária das ocorrências</p><canvas id="c-per"></canvas></div>':'')+
      '<div class="panel"><h2>Distribuição geográfica</h2><p class="sub">Dispersão das coordenadas reportadas</p><canvas id="c-map"></canvas></div>'+
    '</div>';

  // filtros: Ano, Mês, (Período)
  const fb=document.getElementById('db-filtros');
  const anos=['Todos',...P.anos];
  const mkSel=(id,label,opts)=>{
    const w=document.createElement('div'); w.className='fg';
    w.innerHTML='<label>'+label+'</label>';
    const s=document.createElement('select'); s.id=id;
    opts.forEach(o=>{const op=document.createElement('option');op.value=o.v;op.textContent=o.t;s.appendChild(op);});
    w.appendChild(s); fb.appendChild(w); return s;
  };
  mkSel('f-ano','Ano', anos.map(a=>({v:String(a),t:String(a)})));
  mkSel('f-mes','Mês', [{v:'0',t:'Todos'},...MESES_ABR.map((m,i)=>({v:String(i+1),t:m}))]);
  if(P.tem_hora) mkSel('f-per','Período', [{v:'-1',t:'Todos'},...P.periodos_label.map((p,i)=>({v:String(i),t:p}))]);
  const bl=document.createElement('button'); bl.className='btn-limpar'; bl.textContent='Limpar'; fb.appendChild(bl);
  bl.onclick=()=>{['f-ano','f-mes','f-per'].forEach(id=>{const e=document.getElementById(id);if(e)e.selectedIndex=0;});redraw();};
  ['f-ano','f-mes','f-per'].forEach(id=>{const e=document.getElementById(id);if(e)e.onchange=redraw;});

  function redraw(){
    const fa=document.getElementById('f-ano').value;
    const fm=parseInt(document.getElementById('f-mes').value);
    const fpEl=document.getElementById('f-per'); const fp=fpEl?parseInt(fpEl.value):-1;
    // filtra registros: [ano,mes,ruaIdx,perIdx,lat,lng]
    const sel = P.registros.filter(r=>
      (fa==='Todos'||r[0]===parseInt(fa)) &&
      (fm===0||r[1]===fm) &&
      (fp<0||r[3]===fp));
    // KPI badge total
    document.getElementById('db-badge').textContent = fmt(sel.length)+' registros';
    // por mês (12)
    const porMes=Array(12).fill(0); sel.forEach(r=>porMes[r[1]-1]++);
    barChart(document.getElementById('c-mes'), MESES_ABR, porMes);
    // ranking ruas
    const cnt={}; sel.forEach(r=>{cnt[r[2]]=(cnt[r[2]]||0)+1;});
    const top=Object.entries(cnt).sort((a,b)=>b[1]-a[1]).slice(0,15).map(([i,n])=>[P.ruas[i],n]);
    rankingList(document.getElementById('c-rank'), top);
    // período donut
    if(P.tem_hora){
      const pc=[0,0,0,0]; sel.forEach(r=>{if(r[3]>=0)pc[r[3]]++;});
      donut(document.getElementById('c-per'), P.periodos_label, pc);
    }
    // mapa scatter
    const pts=sel.filter(r=>r[4]!=null&&r[5]!=null).map(r=>[r[4],r[5]]);
    scatter(document.getElementById('c-map'), pts);
  }
  window.addEventListener('resize',redraw);
  redraw();
}

/* ========================= MODO: RANKING MENSAL ========================= */
function initRanking(){
  document.getElementById('db-corpo').innerHTML =
    '<div class="panel"><h2>Ranking de vias por congestionamento</h2><p class="sub" id="rk-sub"></p><div class="rank-wrap" id="c-rank"></div></div>';
  const fb=document.getElementById('db-filtros');
  const mkSel=(id,label,opts)=>{
    const w=document.createElement('div'); w.className='fg';
    w.innerHTML='<label>'+label+'</label>';
    const s=document.createElement('select'); s.id=id;
    opts.forEach(o=>{const op=document.createElement('option');op.value=o.v;op.textContent=o.t;s.appendChild(op);});
    w.appendChild(s); fb.appendChild(w); return s;
  };
  const meses = P.chaves_mes.slice().reverse(); // mais recente primeiro
  mkSel('f-mes','Mês', meses.map(k=>({v:k,t:k.replace('_',' ')})));
  mkSel('f-per','Período', P.periodos_ranking.map(p=>({v:p,t:p})));
  ['f-mes','f-per'].forEach(id=>document.getElementById(id).onchange=redraw);

  function redraw(){
    const mk=document.getElementById('f-mes').value;
    const pr=document.getElementById('f-per').value;
    const bloco=(P.dados_ranking[mk]||{})[pr]||[];
    document.getElementById('rk-sub').textContent = mk.replace('_',' ')+' · período '+pr;
    document.getElementById('db-badge').textContent = bloco.length+' vias no ranking';
    const itens=bloco.map(([i,v])=>[P.ruas[i],v]);
    rankingList(document.getElementById('c-rank'), itens);
  }
  redraw();
}

renderKPIs();
if(P.modo==='eventos') initEventos(); else initRanking();
</script>
</body>
</html>
"""
