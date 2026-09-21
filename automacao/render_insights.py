"""
render_insights.py — Gera o slide autocontido "Principais Insights"
(insights.html) a partir do insights.json que cada gerador grava.

Chamado pelo orquestrador (atualizar.py), nunca pelos geradores individuais —
é o único lugar que sabe desenhar o slide, então o visual fica consistente
entre todos os dashboards sem duplicar HTML/CSS em cada gerador.
"""

from __future__ import annotations

import json
from pathlib import Path

_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Principais Insights — __TITULO__</title>
<style>
  :root { --cor: __COR__; }
  html, body {
    margin: 0; padding: 0; width: 100%; height: 100%;
    background: #0b0f14; overflow: hidden;
    font-family: "Segoe UI", -apple-system, Arial, sans-serif;
    display: flex; align-items: center; justify-content: center;
  }
  #painel {
    width: 100%; height: 100%;
    display: flex; flex-direction: column;
    justify-content: center; gap: 3vh;
    padding: 5vh 6vw; box-sizing: border-box;
  }
  #cabecalho {
    display: flex; align-items: center; gap: 16px;
    color: #fff;
  }
  #cabecalho .risco { width: 10px; height: 44px; border-radius: 4px; background: var(--cor); flex: none; }
  #cabecalho h1 { margin: 0; font-size: 2.1vw; font-weight: 700; letter-spacing: .2px; }
  #cabecalho .rotulo {
    margin-left: auto; font-size: 1.1vw; color: rgba(255,255,255,.55);
    text-transform: uppercase; letter-spacing: 1.5px;
  }
  #linhas { display: flex; flex-direction: column; gap: 2.4vh; }
  .linha {
    display: flex; align-items: center; gap: 26px;
    background: rgba(255,255,255,.04);
    border-left: 6px solid var(--cor);
    border-radius: 10px;
    padding: 2.4vh 2.4vw;
  }
  .linha .num { color: var(--cor); font-size: 2.4vw; font-weight: 800; flex: none; line-height: 1; }
  .linha .txt { color: #fff; font-size: 1.9vw; font-weight: 600; line-height: 1.25; }
  #rodape { color: rgba(255,255,255,.35); font-size: .95vw; text-align: right; }
</style>
</head>
<body>
  <div id="painel">
    <div id="cabecalho">
      <span class="risco"></span>
      <h1>Principais Insights</h1>
      <span class="rotulo">__TITULO__</span>
    </div>
    <div id="linhas">
__LINHAS__
    </div>
    <div id="rodape">Atualizado em __GERADO_EM__</div>
  </div>
</body>
</html>
"""

_LINHA_TEMPLATE = """      <div class="linha"><span class="num">{i}</span><span class="txt">{texto}</span></div>"""


def _escapar(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def renderizar(pasta_portal_dashboard: Path, insights_json: Path, log=None) -> Path | None:
    """Lê insights_json e escreve insights.html dentro de
    pasta_portal_dashboard. Retorna o caminho gerado, ou None se
    insights_json não existir. Nunca lança exceção — quem chama decide se
    loga o erro; uma falha aqui não pode derrubar a publicação."""
    if not insights_json.exists():
        return None

    dados = json.loads(insights_json.read_text(encoding="utf-8"))
    titulo = dados.get("titulo", "")
    cor = dados.get("cor", "#f5a623")
    gerado_em = dados.get("gerado_em", "")
    linhas = dados.get("linhas", [])[:5]

    linhas_html = "\n".join(
        _LINHA_TEMPLATE.format(i=i + 1, texto=_escapar(str(t)))
        for i, t in enumerate(linhas)
    )

    html = (
        _TEMPLATE
        .replace("__TITULO__", _escapar(titulo))
        .replace("__COR__", cor)
        .replace("__LINHAS__", linhas_html)
        .replace("__GERADO_EM__", _escapar(gerado_em))
    )

    pasta_portal_dashboard.mkdir(parents=True, exist_ok=True)
    saida = pasta_portal_dashboard / "insights.html"
    saida.write_text(html, encoding="utf-8")
    if log:
        log(f"  Insights: {len(linhas)} destaques publicados em {saida.name}")
    return saida
