"""
periodo_dados.py — Linha "Período dos dados" abaixo do título de cada painel.

Lê as datas dos dados embutidos na própria página do Portal (depois da
integração) e grava/atualiza, logo abaixo do <h1 class="pbi-page-title">:

    <p class="pbi-periodo-dados">Período dos dados: <strong>…</strong></p>

Assim o período acompanha cada atualização, sem texto fixo para manter.
Só as páginas listadas em EXTRATORES recebem a linha; as demais são ignoradas.
"""
from __future__ import annotations

import json
import re
from datetime import date, timedelta

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _json_apos(html: str, marcador: str):
    i = html.find(marcador)
    if i < 0:
        return None
    return json.JSONDecoder().raw_decode(html[i + len(marcador):].lstrip())[0]


def _iso(datas) -> tuple[date, date] | None:
    ds = sorted(date.fromisoformat(d[:10]) for d in datas if d)
    return (ds[0], ds[-1]) if ds else None


def _const_d(html):            # Waze Acidentes / Buracos: const D={"dates":[...]}
    d = _json_apos(html, "const D=")
    return _iso(d["dates"]) if d else None


def _alertas(html):            # Waze Alertas: const RECORDS = [{"data": "AAAA-MM-DD", ...}]
    d = _json_apos(html, "const RECORDS =")
    return _iso(r["data"] for r in d) if d else None


def _congestionamentos(html):  # Waze Congestionamentos: <script type="application/json">{"dates":[...]}
    m = re.search(r'<script[^>]*type="application/json"[^>]*>\s*(\{"nfiles".*?)</script>', html, re.S)
    return _iso(json.loads(m.group(1))["dates"]) if m else None


def _transporte(html):         # Transporte: meses = [[ano, mes, passageiros], ...] -> granularidade mensal
    d = _json_apos(html, '<script id="dashboard-data" type="application/json">')
    if not d or not d.get("meses"):
        return None
    ms = sorted((a, m) for a, m, *_ in d["meses"])
    return ("mes", ms[0], ms[-1])


def _acidentes(html):          # Acidentes Bombeiros: DATA.base + coluna d (dias desde a base)
    d = _json_apos(html, "const DATA =")
    if not d:
        return None
    base, col = date.fromisoformat(d["base"]), d["cols"]["d"]
    return base + timedelta(days=min(col)), base + timedelta(days=max(col))


EXTRATORES = {
    "dashboards/waze/acidentes/index.html": _const_d,
    "dashboards/waze/buracos/index.html": _const_d,
    "dashboards/waze/alertas/index.html": _alertas,
    "dashboards/waze/ranqueamento/congestionamentos/index.html": _congestionamentos,
    "dashboards/transporte/index.html": _transporte,
    "dashboards/acidentes/index.html": _acidentes,
}


def formatar(periodo) -> str:
    if periodo[0] == "mes":
        (a0, m0), (a1, m1) = periodo[1], periodo[2]
        return f"{MESES[m0 - 1]}/{a0} a {MESES[m1 - 1]}/{a1}"
    ini, fim = periodo
    if (fim - ini).days <= 62:       # períodos curtos: dia a dia
        return f"{ini:%d/%m/%Y} a {fim:%d/%m/%Y}"
    return (f"{MESES[ini.month - 1]}/{ini.year} a {MESES[fim.month - 1]}/{fim.year} "
            f"(último registro em {fim:%d/%m/%Y})")


def atualizar(portal_dir, destino_rel: str, log) -> None:
    extrator = EXTRATORES.get(destino_rel)
    if not extrator:
        return
    pagina = portal_dir / destino_rel
    html = pagina.read_text(encoding="utf-8")
    try:
        periodo = extrator(html)
    except Exception as e:  # dado com formato inesperado: avisa, mas não derruba a publicação
        log(f"  [aviso] Periodo dos dados nao calculado ({destino_rel}): {e}")
        return
    if not periodo:
        log(f"  [aviso] Periodo dos dados nao encontrado nos dados de {destino_rel}")
        return
    linha = f'<p class="pbi-periodo-dados">Período dos dados: <strong>{formatar(periodo)}</strong></p>'
    novo = re.sub(r'\n\s*<p class="pbi-periodo-dados">.*?</p>', "", html, count=1)
    novo, n = re.subn(r'(\n(\s*)<h1 class="pbi-page-title">.*?</h1>)',
                      lambda m: m.group(1) + "\n" + m.group(2) + linha, novo, count=1)
    if n != 1:
        log(f"  [aviso] Titulo da pagina nao encontrado para gravar o periodo ({destino_rel})")
        return
    if novo != html:
        pagina.write_text(novo, encoding="utf-8")
    log(f"Periodo dos dados: {formatar(periodo)}")
