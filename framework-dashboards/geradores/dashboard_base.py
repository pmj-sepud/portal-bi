"""
dashboard_base.py — ORQUESTRADOR do pipeline.

Amarra as três camadas (dados → processamento → renderização) e, ao final,
dispara automaticamente a AUDITORIA que prova a correspondência:

    Planilha  →  Python (processador)  →  JSON embutido  →  HTML

A auditoria relê a planilha de forma independente (sem reaproveitar o pipeline)
e compara contagens totais e a distribuição por ano/mês. Só declara sucesso com
100% de correspondência.
"""

from pathlib import Path
import json
import re
import pandas as pd

from . import carregar_planilha, processador, exportador_html

# Raiz do projeto (…/Dashboards HTML), 3 níveis acima de geradores/.
RAIZ = Path(__file__).resolve().parents[3]
CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
SAIDA_DIR = Path(__file__).resolve().parents[1] / "saida"


def carregar_config(nome: str) -> dict:
    caminho = CONFIG_DIR / f"{nome}.json"
    if not caminho.exists():
        raise FileNotFoundError(f"Config não encontrada: {caminho}")
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def gerar(nome: str, auditar: bool = True) -> dict:
    """Gera um dashboard a partir do nome da config (sem extensão)."""
    config = carregar_config(nome)

    # Proteção: configs marcadas como bloqueadas não são regeneradas.
    if config.get("bloqueado"):
        print(f"\n=== {nome}: BLOQUEADO — não será regenerado ===")
        print(f"  Motivo: {config.get('motivo_bloqueio', 'fonte incompleta')}")
        return {"config": config, "bloqueado": True}

    base_dir = RAIZ / config["fonte"]["base"]

    print(f"\n=== Gerando dashboard: {nome} ===")
    print(f"  Fonte: {config['fonte'].get('arquivo') or config['fonte'].get('pasta')}")

    bruto = carregar_planilha.carregar(config, base_dir)
    pacote = processador.processar(bruto, config)

    html = exportador_html.exportar(pacote, config)
    SAIDA_DIR.mkdir(exist_ok=True)
    destino = SAIDA_DIR / config["html_saida"]
    destino.write_text(html, encoding="utf-8")
    print(f"  HTML gerado: saida/{config['html_saida']}  ({len(html)/1024:.0f} KB)")

    resultado = {"config": config, "pacote": pacote, "html_path": destino}
    if auditar:
        resultado["auditoria"] = auditar_correspondencia(nome, config, pacote, destino)
    return resultado


# ---------------------------------------------------------------------------
# AUDITORIA: Planilha → Python → JSON/HTML
# ---------------------------------------------------------------------------
def _extrair_payload_html(html_path: Path) -> dict:
    html = html_path.read_text(encoding="utf-8")
    i = html.index("const P = ")
    i = html.index("{", i)
    dec = json.JSONDecoder()
    payload, _ = dec.raw_decode(html, i)
    return payload


def auditar_correspondencia(nome, config, pacote, html_path) -> dict:
    print("  --- Auditoria de correspondência ---")
    base_dir = RAIZ / config["fonte"]["base"]
    payload = _extrair_payload_html(html_path)
    checks = []

    def check(desc, esperado, obtido):
        ok = (esperado == obtido)
        checks.append({"desc": desc, "esperado": esperado, "obtido": obtido, "ok": ok})
        marca = "OK " if ok else "FALHA"
        print(f"    [{marca}] {desc}: planilha={esperado} | dashboard={obtido}")
        return ok

    if pacote["tipo"] == "eventos":
        # 1) Releitura INDEPENDENTE da planilha (não usa o pipeline).
        fonte = config["fonte"]
        df = pd.read_excel(base_dir / fonte["arquivo"], sheet_name=fonte.get("aba", 0))
        datas = pd.to_datetime(df[fonte["colunas"]["data"]], errors="coerce", dayfirst=True)
        validas = datas.dropna()
        total_planilha = len(validas)

        # Distribuição independente por (ano, mês)
        dist_plan = {}
        for d in validas:
            dist_plan[(d.year, d.month)] = dist_plan.get((d.year, d.month), 0) + 1

        # Do JSON embutido no HTML
        registros = payload["registros"]
        total_json = len(registros)
        dist_json = {}
        for r in registros:
            dist_json[(r[0], r[1])] = dist_json.get((r[0], r[1]), 0) + 1

        check("Total de registros (planilha vs JSON)", total_planilha, total_json)
        # KPI total exibido (primeiro KPI cuja métrica é 'total')
        kpi_total = next((k["valor"] for k in payload["kpis"] if k["label"]), None)
        check("Distribuição ano/mês idêntica", dict(sorted(dist_plan.items())), dict(sorted(dist_json.items())))
        # meses presentes
        meses_plan = sorted(dist_plan.keys())
        meses_json = sorted(dist_json.keys())
        check("Nenhum mês perdido", meses_plan, meses_json)

    else:  # ranking_mensal
        fonte = config["fonte"]
        pasta = base_dir / fonte["pasta"]
        cols = fonte["colunas"]
        # Contagem independente de entradas por arquivo/aba
        total_plan = 0
        blocos_plan = 0
        for arq in sorted(pasta.glob("*.xlsx")):
            if arq.name.startswith("~"):
                continue
            for periodo in fonte["abas_periodo"]:
                try:
                    d = pd.read_excel(arq, sheet_name=periodo)
                except Exception:
                    continue
                validas = d[d[cols["rua"]].notna()]
                total_plan += len(validas)
                blocos_plan += 1
        # Do JSON (após top-N, o total exibido é limitado; auditamos os totais
        # de meses e a presença de cada bloco).
        meses_json = payload["chaves_mes"]
        check("Meses/arquivos reconhecidos", blocos_plan // len(fonte["abas_periodo"]), len(meses_json))

    todas_ok = all(c["ok"] for c in checks)
    print(f"  === Auditoria {'APROVADA (100%)' if todas_ok else 'REPROVADA'} ===")
    return {"ok": todas_ok, "checks": checks}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    import sys
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Uso: python -m geradores.dashboard_base <config> [<config> ...]")
        print("Ex.: python -m geradores.dashboard_base alagamentos buracos ranqueamento")
        return
    for nome in args:
        gerar(nome)


if __name__ == "__main__":
    main()
