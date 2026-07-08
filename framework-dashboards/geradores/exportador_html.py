"""
exportador_html.py — Camada de RENDERIZAÇÃO.

Renderiza o pacote processado usando o DESIGN SYSTEM oficial do Portal BI
(assets/css/bi-dashboard-system.css), cuja referência é o dashboard
"Acidentes Bombeiros UMO". O CSS do design system é lido e embutido no momento
da geração (fonte única de verdade, sem código duplicado, saída autossuficiente).

A identidade de cada categoria muda apenas pela cor (--acc-*) e pelo ícone/título
vindos da configuração. Estrutura, espaçamentos, tipografia, cards KPI, cards de
gráfico, barra de filtros e rodapé são idênticos em todos os dashboards.
"""

import json
from pathlib import Path

# Design system canônico (mesmo arquivo usado por todo o portal).
_CSS_PATH = Path(__file__).resolve().parents[2] / "assets" / "css" / "bi-dashboard-system.css"


def exportar(pacote: dict, config: dict) -> str:
    cor = config.get("cor", {})
    payload = {
        "modo": pacote["tipo"],
        "titulo": config["titulo"],
        "subtitulo": config["subtitulo"],
        "icone": config.get("icone", "📊"),
        "kpis": pacote["kpis"],
        "ruas": pacote["ruas"],
        "graficos_cfg": config.get("graficos", {}),
    }
    if pacote["tipo"] == "eventos":
        payload.update({
            "registros": pacote["registros"],
            "anos": pacote["anos"],
            "periodos_label": pacote["periodos_label"],
            "tem_hora": pacote["tem_hora"],
        })
    else:
        payload.update({
            "dados_ranking": pacote["dados_ranking"],
            "chaves_mes": pacote["chaves_mes"],
            "periodos_ranking": pacote["periodos_ranking"],
        })

    dados_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    css = _CSS_PATH.read_text(encoding="utf-8")

    return (
        _TEMPLATE
        .replace("/*__CSS__*/", css)
        .replace("__ACC_DARK__", cor.get("escura", "#0b3a5e"))
        .replace("__ACC_MID__", cor.get("primaria", "#14508a"))
        .replace("__ACC_MAIN__", cor.get("primaria", "#1a5b9c"))
        .replace("__ACC_LIGHT__", cor.get("clara", "#4a90d9"))
        .replace("/*__DADOS__*/", dados_json)
    )


_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Dashboard — Portal de BI Joinville</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
/*__CSS__*/
/* Cor da categoria (única diferença entre dashboards) + tints derivados */
.bi-dash{
  --acc-dark:__ACC_DARK__; --acc-mid:__ACC_MID__; --acc-main:__ACC_MAIN__; --acc-light:__ACC_LIGHT__;
  --acc-pale:color-mix(in srgb, var(--acc-main) 9%, #ffffff);
  --acc-border:color-mix(in srgb, var(--acc-main) 20%, #ffffff);
}
</style>
</head>
<body>
<div class="bi-dash">
  <div class="bi-header">
    <div class="bi-brand">
      <div class="bi-ic" id="bi-ic"></div>
      <div><h1 id="bi-titulo"></h1><span id="bi-sub"></span></div>
    </div>
    <div class="bi-header-right">
      <div class="bi-badge"><span class="bi-live"></span><span id="bi-badge">—</span></div>
    </div>
  </div>
  <div class="bi-filterbar" id="bi-filtros"></div>
  <div class="bi-body">
    <div class="bi-section-label">Indicadores gerais</div>
    <div class="bi-kpi-grid" id="bi-kpis"></div>
    <div class="bi-section-label">Análise e distribuição</div>
    <div id="bi-corpo"></div>
  </div>
  <div class="bi-foot">Gerado pelo Framework de Dashboards · Portal de BI · Prefeitura de Joinville · dados 1:1 com a planilha de origem.</div>
</div>

<script>
const P = /*__DADOS__*/;
const R = document.querySelector('.bi-dash');
document.getElementById('bi-ic').textContent = P.icone;
document.getElementById('bi-titulo').textContent = P.titulo;
document.getElementById('bi-sub').textContent = P.subtitulo;
const MESES_ABR=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
const fmt=n=>(typeof n==='number')?n.toLocaleString('pt-BR'):n;
const acc=()=>getComputedStyle(R).getPropertyValue('--acc-main').trim();
const accD=()=>getComputedStyle(R).getPropertyValue('--acc-dark').trim();
const accL=()=>getComputedStyle(R).getPropertyValue('--acc-light').trim();

function setupCanvas(cv,h){const dpr=window.devicePixelRatio||1;const w=cv.clientWidth||cv.parentNode.clientWidth-24;cv.width=w*dpr;cv.height=h*dpr;cv.style.height=h+'px';const c=cv.getContext('2d');c.scale(dpr,dpr);return{ctx:c,w,h};}
function barChart(cv,labels,values){
  const {ctx,w,h}=setupCanvas(cv,300);ctx.clearRect(0,0,w,h);
  const pad={l:46,r:12,t:14,b:34},max=Math.max(1,...values),bw=(w-pad.l-pad.r)/values.length;
  ctx.font="10px 'DM Mono',monospace";ctx.textAlign='right';
  for(let g=0;g<=4;g++){const y=h-pad.b-(h-pad.t-pad.b)*g/4;ctx.strokeStyle='#eef2f7';ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(w-pad.r,y);ctx.stroke();ctx.fillStyle='#9ca3af';ctx.fillText(Math.round(max*g/4).toLocaleString('pt-BR'),pad.l-6,y+3);}
  for(let i=0;i<values.length;i++){const bh=(h-pad.t-pad.b)*values[i]/max,x=pad.l+bw*i+bw*0.18,y=h-pad.b-bh;
    const grd=ctx.createLinearGradient(0,y,0,h-pad.b);grd.addColorStop(0,accL());grd.addColorStop(1,acc());
    ctx.fillStyle=grd;ctx.fillRect(x,y,bw*0.64,bh);
    ctx.fillStyle='#9ca3af';ctx.font="10px 'DM Sans',sans-serif";ctx.textAlign='center';ctx.fillText(labels[i],pad.l+bw*i+bw/2,h-pad.b+14);}
}
function donut(cv,labels,values){
  const {ctx,w,h}=setupCanvas(cv,220);ctx.clearRect(0,0,w,h);
  const total=values.reduce((a,b)=>a+b,0)||1,cx=104,cy=h/2,r=70,ir=44;
  const cols=[accD(),acc(),accL(),'#c7ddf3'];let ang=-Math.PI/2;
  for(let i=0;i<values.length;i++){const a2=ang+2*Math.PI*values[i]/total;ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,r,ang,a2);ctx.closePath();ctx.fillStyle=cols[i%cols.length];ctx.fill();ang=a2;}
  ctx.globalCompositeOperation='destination-out';ctx.beginPath();ctx.arc(cx,cy,ir,0,6.29);ctx.fill();ctx.globalCompositeOperation='source-over';
  ctx.fillStyle='#111827';ctx.textAlign='center';ctx.font="700 15px 'DM Mono',monospace";ctx.fillText(fmt(total),cx,cy+5);
  let ly=26;for(let i=0;i<labels.length;i++){ctx.fillStyle=cols[i%cols.length];ctx.fillRect(196,ly-8,10,10);ctx.fillStyle='#374151';ctx.textAlign='left';ctx.font="11px 'DM Sans',sans-serif";const pct=((values[i]/total)*100).toFixed(1);ctx.fillText(labels[i]+'  '+fmt(values[i])+' ('+pct+'%)',212,ly);ly+=22;}
}
function scatter(cv,pts){
  const {ctx,w,h}=setupCanvas(cv,300);ctx.clearRect(0,0,w,h);
  if(!pts.length){ctx.fillStyle='#9ca3af';ctx.font="12px 'DM Sans'";ctx.fillText('Sem coordenadas para o filtro atual',14,24);return;}
  // Extremos via laço (evita estouro de pilha do spread em bases grandes).
  let laMin=Infinity,laMax=-Infinity,lnMin=Infinity,lnMax=-Infinity;
  for(let i=0;i<pts.length;i++){const p=pts[i];if(p[0]<laMin)laMin=p[0];if(p[0]>laMax)laMax=p[0];if(p[1]<lnMin)lnMin=p[1];if(p[1]>lnMax)lnMax=p[1];}
  const pad=14;
  // Amostragem apenas para o desenho (KPIs e contagens usam 100% dos dados).
  const step=pts.length>8000?Math.ceil(pts.length/8000):1;
  ctx.fillStyle=acc();ctx.globalAlpha=.3;
  for(let i=0;i<pts.length;i+=step){const p=pts[i];const x=pad+(w-2*pad)*(p[1]-lnMin)/((lnMax-lnMin)||1),y=pad+(h-2*pad)*(1-(p[0]-laMin)/((laMax-laMin)||1));ctx.beginPath();ctx.arc(x,y,2.3,0,6.28);ctx.fill();}
  ctx.globalAlpha=1;
  if(step>1){ctx.globalAlpha=1;ctx.fillStyle='#8493a6';ctx.font="10px 'DM Sans'";ctx.textAlign='right';ctx.fillText('amostra visual de '+fmt(pts.length)+' pontos',w-6,h-6);}
}
function rankingList(el,itens){
  el.innerHTML='';
  if(!itens.length){el.innerHTML='<div class="bi-empty">Sem dados para o filtro atual.</div>';return;}
  const mx=Math.max(1,...itens.map(i=>i[1]));
  itens.forEach((it,idx)=>{const row=document.createElement('div');row.className='bi-rank-row';
    row.innerHTML='<div class="bi-rank-num">'+(idx+1)+'</div>'+
      '<div class="bi-rank-label" title="'+it[0]+'">'+it[0]+'</div>'+
      '<div class="bi-rank-wrap"><div class="bi-rank-bar" style="width:'+(100*it[1]/mx)+'%"></div></div>'+
      '<div class="bi-rank-val">'+fmt(it[1])+'</div>';el.appendChild(row);});
}
function renderKPIs(){
  const box=document.getElementById('bi-kpis');box.innerHTML='';
  P.kpis.forEach(k=>{let v=k.valor;if(k.formato==='int'&&typeof v==='number')v=fmt(v);
    const sm=(k.formato!=='int')?' sm':'';
    const d=document.createElement('div');d.className='bi-kpi';
    d.innerHTML='<div class="bi-kpi-ic">'+(k.icone||'📊')+'</div>'+
      '<div class="bi-kpi-txt"><div class="bi-kpi-label">'+k.label+'</div>'+
      '<div class="bi-kpi-value'+sm+'" title="'+v+'">'+v+(k.sufixo||'')+'</div></div>';
    box.appendChild(d);});
}
function mkSel(fb,id,label,opts){const w=document.createElement('div');w.className='bi-fg';w.innerHTML='<label>'+label+'</label>';const s=document.createElement('select');s.id=id;opts.forEach(o=>{const op=document.createElement('option');op.value=o.v;op.textContent=o.t;s.appendChild(op);});w.appendChild(s);fb.appendChild(w);return s;}

/* ============================ EVENTOS ============================ */
function initEventos(){
  document.getElementById('bi-corpo').innerHTML=
    '<div class="bi-grid">'+
      '<div class="bi-chart"><div class="bi-chart-head"><div class="bi-chart-title"><span class="bi-dot"></span>Ocorrências por mês</div><div class="bi-chart-sub">Distribuição mensal no período selecionado</div></div><div class="bi-chart-body"><canvas id="c-mes"></canvas></div></div>'+
      '<div class="bi-chart"><div class="bi-chart-head"><div class="bi-chart-title"><span class="bi-dot"></span>Ranking de vias</div><div class="bi-chart-sub">Top vias por volume de registros</div></div><div class="bi-chart-body" id="c-rank"></div></div>'+
    '</div>'+
    '<div class="bi-grid equal">'+
      (P.tem_hora?'<div class="bi-chart"><div class="bi-chart-head"><div class="bi-chart-title"><span class="bi-dot"></span>Por período do dia</div><div class="bi-chart-sub">Faixa horária das ocorrências</div></div><div class="bi-chart-body"><canvas id="c-per"></canvas></div></div>':'')+
      '<div class="bi-chart"><div class="bi-chart-head"><div class="bi-chart-title"><span class="bi-dot"></span>Distribuição geográfica</div><div class="bi-chart-sub">Dispersão das coordenadas reportadas</div></div><div class="bi-chart-body"><canvas id="c-map"></canvas></div></div>'+
    '</div>';
  const fb=document.getElementById('bi-filtros');
  mkSel(fb,'f-ano','Ano',['Todos',...P.anos].map(a=>({v:String(a),t:String(a)})));
  mkSel(fb,'f-mes','Mês',[{v:'0',t:'Todos'},...MESES_ABR.map((m,i)=>({v:String(i+1),t:m}))]);
  if(P.tem_hora)mkSel(fb,'f-per','Período',[{v:'-1',t:'Todos'},...P.periodos_label.map((p,i)=>({v:String(i),t:p}))]);
  const sep=document.createElement('div');sep.className='bi-filter-sep';fb.appendChild(sep);
  const bl=document.createElement('button');bl.className='bi-btn-clear';bl.textContent='Limpar filtros';fb.appendChild(bl);
  bl.onclick=()=>{['f-ano','f-mes','f-per'].forEach(id=>{const e=document.getElementById(id);if(e)e.selectedIndex=0;});redraw();};
  ['f-ano','f-mes','f-per'].forEach(id=>{const e=document.getElementById(id);if(e)e.onchange=redraw;});
  function redraw(){
    const fa=document.getElementById('f-ano').value,fm=parseInt(document.getElementById('f-mes').value);
    const fpEl=document.getElementById('f-per'),fp=fpEl?parseInt(fpEl.value):-1;
    const sel=P.registros.filter(r=>(fa==='Todos'||r[0]===parseInt(fa))&&(fm===0||r[1]===fm)&&(fp<0||r[3]===fp));
    document.getElementById('bi-badge').textContent=fmt(sel.length)+' registros';
    const porMes=Array(12).fill(0);sel.forEach(r=>porMes[r[1]-1]++);barChart(document.getElementById('c-mes'),MESES_ABR,porMes);
    const cnt={};sel.forEach(r=>{cnt[r[2]]=(cnt[r[2]]||0)+1;});
    rankingList(document.getElementById('c-rank'),Object.entries(cnt).sort((a,b)=>b[1]-a[1]).slice(0,15).map(([i,n])=>[P.ruas[i],n]));
    if(P.tem_hora){const pc=[0,0,0,0];sel.forEach(r=>{if(r[3]>=0)pc[r[3]]++;});donut(document.getElementById('c-per'),P.periodos_label,pc);}
    scatter(document.getElementById('c-map'),sel.filter(r=>r[4]!=null&&r[5]!=null).map(r=>[r[4],r[5]]));
  }
  window.addEventListener('resize',redraw);redraw();
}

/* ========================= RANKING MENSAL ========================= */
function initRanking(){
  document.getElementById('bi-corpo').innerHTML=
    '<div class="bi-chart"><div class="bi-chart-head"><div class="bi-chart-title"><span class="bi-dot"></span>Ranking de vias por congestionamento</div><div class="bi-chart-sub" id="rk-sub"></div></div><div class="bi-chart-body" id="c-rank"></div></div>';
  const fb=document.getElementById('bi-filtros');
  mkSel(fb,'f-mes','Mês',P.chaves_mes.slice().reverse().map(k=>({v:k,t:k.replace('_',' ')})));
  mkSel(fb,'f-per','Período',P.periodos_ranking.map(p=>({v:p,t:p})));
  ['f-mes','f-per'].forEach(id=>document.getElementById(id).onchange=redraw);
  function redraw(){
    const mk=document.getElementById('f-mes').value,pr=document.getElementById('f-per').value;
    const bloco=(P.dados_ranking[mk]||{})[pr]||[];
    document.getElementById('rk-sub').textContent=mk.replace('_',' ')+' · período '+pr;
    document.getElementById('bi-badge').textContent=bloco.length+' vias';
    rankingList(document.getElementById('c-rank'),bloco.map(([i,v])=>[P.ruas[i],v]));
  }
  redraw();
}

renderKPIs();
if(P.modo==='eventos')initEventos();else initRanking();
</script>
</body>
</html>
"""
