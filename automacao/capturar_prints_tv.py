#!/usr/bin/env python3
"""
capturar_prints_tv.py — Gera os "prints" (PNG) usados pelo Modo TV no lugar
do iframe ao vivo em cada dashboard da rotacao.

Abre cada dashboard localmente (Chromium headless via Playwright), esconde o
chrome do Portal (navbar/breadcrumb/rodape) exatamente como o tv.html faz em
tempo real, espera os graficos renderizarem e tira um screenshot 1920x1080.

Uso:
    python capturar_prints_tv.py            # recaptura todos os prints da TV
    python capturar_prints_tv.py acidentes waze-alertas   # so os informados
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PORTAL = Path(__file__).resolve().parent.parent
SAIDA = PORTAL / "assets" / "images" / "tv-prints"

# Mesma selecao da rotacao padrao do tv.html (ver IDS_PADRAO / SUBPAINEIS_WAZE).
DASHBOARDS = [
    ("acidentes", "dashboards/acidentes/index.html"),
    ("radares", "dashboards/radares/index.html"),
    ("transporte", "dashboards/transporte/index.html"),
    ("waze-acidentes", "dashboards/waze/acidentes/index.html"),
    ("waze-alagamentos", "dashboards/waze/alagamentos/index.html"),
    ("waze-alertas", "dashboards/waze/alertas/index.html"),
    ("waze-buracos", "dashboards/waze/buracos/index.html"),
    ("waze-ranqueamento", "dashboards/waze/ranqueamento/index.html"),
    ("rede-cicloviaria", "dashboards/rede-cicloviaria/index.html"),
]

ESCONDER_CHROME_CSS = (
    ".pbi-chrome, .pbi-footer, .pbi-breadcrumb-wrap ol "
    "{ display: none !important; }"
)


def capturar(pw, dashboard_id: str, caminho_rel: str) -> None:
    origem = PORTAL / caminho_rel
    if not origem.exists():
        print(f"  [PULADO] {dashboard_id}: arquivo nao encontrado ({caminho_rel})")
        return

    navegador = pw.chromium.launch()
    pagina = navegador.new_page(viewport={"width": 1920, "height": 1080})
    try:
        pagina.goto(origem.as_uri(), wait_until="networkidle", timeout=30000)
        pagina.add_style_tag(content=ESCONDER_CHROME_CSS)
        pagina.wait_for_timeout(1800)  # animações/charts terminarem de desenhar

        SAIDA.mkdir(parents=True, exist_ok=True)
        destino = SAIDA / f"{dashboard_id}.png"
        pagina.screenshot(path=str(destino))
        print(f"  [OK] {dashboard_id} -> {destino.relative_to(PORTAL)}")
    except Exception as e:
        print(f"  [FALHA] {dashboard_id}: {e}")
    finally:
        navegador.close()


def main() -> int:
    filtro = set(sys.argv[1:]) or None
    alvos = [d for d in DASHBOARDS if not filtro or d[0] in filtro]
    if not alvos:
        print("Nenhum dashboard valido informado.")
        print("Validos: " + ", ".join(d[0] for d in DASHBOARDS))
        return 1

    print(f"Capturando {len(alvos)} print(s) para o Modo TV...\n")
    with sync_playwright() as pw:
        for dashboard_id, caminho_rel in alvos:
            capturar(pw, dashboard_id, caminho_rel)
    print("\nConcluido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
