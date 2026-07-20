#!/usr/bin/env python3
"""
atualizar.py — Atualiza UM dashboard do Portal BI, de ponta a ponta.

    Planilha -> Gerador oficial -> Auditoria -> Portal -> Catálogo
             -> Git (commit/push) -> GitHub Pages -> Navegador

Uso (normalmente chamado pelo .BAT da pasta do dashboard):

    python atualizar.py <dashboard_id>
    python atualizar.py processos --sem-publicar     (teste: nao faz git/push)
    python atualizar.py waze --sem-navegador

Se a auditoria acusar divergência, NADA é publicado.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comum as C
from registro import obter, REGISTRO


# --------------------------------------------------------------- BESPOKE
def _executar_bespoke(cfg: dict, log: C.Log) -> dict:
    pasta = C.DADOS / cfg["pasta"]
    planilha = C.localizar_planilha(pasta, cfg.get("planilha"), log)
    log(f"Planilha : {planilha.name}")
    log(f"Pasta    : {pasta.relative_to(C.RAIZ)}")

    _, contagem = C.rodar_gerador(pasta, cfg["gerador"], log)
    html_gerado = pasta / cfg["html_gerado"]
    total = C.auditar_bespoke(html_gerado, contagem, log)

    C.integrar_no_portal(html_gerado, cfg["portal"], cfg["profundidade"], log)
    if cfg.get("reskin"):
        C.aplicar_reskin(cfg["portal"], cfg["reskin"], log)

    return {"paineis": {cfg["painel"]: total} if total else {}, "planilhas": [planilha.name], "total": total}


# ---------------------------------------------------------------- PORTAL
def _executar_portal(cfg: dict, log: C.Log) -> dict:
    """Dashboard cujo gerador reescreve o bloco de dados direto na página do
    Portal (não há HTML intermediário nem etapa de integração/reskin)."""
    pasta = C.DADOS / cfg["pasta"]
    planilha = C.localizar_planilha(pasta, cfg.get("planilha"), log)
    log(f"Planilha : {planilha.name}")
    log(f"Pasta    : {pasta.relative_to(C.RAIZ)}")

    _, contagem = C.rodar_gerador(pasta, cfg["gerador"], log)
    portal_html = C.PORTAL / cfg["portal"]
    total = C.auditar_bespoke(portal_html, contagem, log)
    log(f"Pagina do Portal atualizada: {cfg['portal']}")

    return {"paineis": {cfg["painel"]: total} if total else {}, "planilhas": [planilha.name], "total": total}


# ------------------------------------------------------------- FRAMEWORK
def _executar_framework(cfg: dict, log: C.Log) -> dict:
    sys.path.insert(0, str(C.FRAMEWORK))
    try:
        from geradores import dashboard_base  # type: ignore
    except Exception as e:  # pragma: no cover
        raise C.FalhaAutomacao(f"NAO FOI POSSIVEL CARREGAR O FRAMEWORK BI:\n  {e}")

    paineis: dict[str, int] = {}
    planilhas: list[str] = []
    total_geral = 0

    for sub in cfg["subpaineis"]:
        nome = sub["config"]
        log("")
        log(f"--- Framework: {nome} ---")
        resultado = dashboard_base.gerar(nome)          # gera + audita internamente

        if resultado.get("bloqueado"):
            log(f"  BLOQUEADO: {resultado['config'].get('motivo_bloqueio', '')}")
            continue

        auditoria = resultado.get("auditoria", {})
        if not auditoria.get("ok"):
            raise C.FalhaAutomacao(
                f"DIVERGENCIA NA AUDITORIA DO DASHBOARD '{nome}' — PUBLICACAO ABORTADA.\n"
                "  Nada foi publicado. Confira a planilha de origem."
            )
        log("  [OK] Auditoria 100% (planilha -> framework -> dashboard)")

        fonte = resultado["config"]["fonte"]
        planilhas.append(fonte.get("arquivo") or fonte.get("pasta", nome))

        html_gerado = C.FRAMEWORK / "saida" / sub["html_gerado"]
        C.integrar_no_portal(html_gerado, sub["portal"], sub["profundidade"], log)

        metrics = resultado["pacote"].get("metrics", {})
        total = metrics.get("total")
        if isinstance(total, int):
            paineis[sub["painel"]] = total
            total_geral += total
            log(f"  Registros: {total:,}".replace(",", "."))

    if not paineis:
        raise C.FalhaAutomacao("Nenhum sub-painel foi gerado com sucesso.")
    return {"paineis": paineis, "planilhas": planilhas, "total": total_geral}


# ---------------------------------------------------------------- MANUAL
def _executar_manual(cfg: dict, log: C.Log) -> dict:
    log("")
    log("AVISO: " + cfg.get("nota", ""))
    pasta = C.DADOS / cfg["pasta"]
    html_origem = pasta / cfg["html_gerado"]
    if not html_origem.exists():
        raise C.FalhaAutomacao(f"HTML DE ORIGEM NAO ENCONTRADO:\n  {html_origem}")
    log(f"Republicando HTML de origem: {html_origem.name}")
    C.integrar_no_portal(html_origem, cfg["portal"], cfg["profundidade"], log)
    if cfg.get("reskin"):
        C.aplicar_reskin(cfg["portal"], cfg["reskin"], log)
    return {"paineis": {}, "planilhas": [], "total": None}


# ------------------------------------------------------------ ORQUESTRAÇÃO
def executar(dashboard_id: str, log: C.Log, publicar: bool = True, navegador: bool = True) -> dict:
    cfg = obter(dashboard_id)
    log.titulo(f"ATUALIZANDO: {cfg['titulo']}")
    C.checar_prerequisitos(log)
    log("")

    tipo = cfg["tipo"]
    if tipo == "placeholder":
        log("Este dashboard ainda nao possui dados/painel.")
        log("Nota: " + cfg.get("nota", ""))
        return {"id": dashboard_id, "titulo": cfg["titulo"], "status": "ignorado",
                "paineis": {}, "planilhas": [], "total": None}

    if tipo == "portal":
        r = _executar_portal(cfg, log)
    elif tipo == "bespoke":
        r = _executar_bespoke(cfg, log)
    elif tipo == "framework":
        r = _executar_framework(cfg, log)
    elif tipo == "manual":
        r = _executar_manual(cfg, log)
    else:
        raise C.FalhaAutomacao(f"Tipo de dashboard desconhecido: {tipo}")

    if cfg.get("nota") and tipo != "manual":
        log("")
        log("Nota: " + cfg["nota"])

    # Centro de Operações (apenas dados)
    log("")
    log("--- Centro de Operacoes (catalog.js) ---")
    C.atualizar_catalog(r["paineis"], cfg.get("categoria"), log)

    resultado = {"id": dashboard_id, "titulo": cfg["titulo"], "status": "atualizado", **r}

    if publicar:
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        msg = f"Atualizacao automatica - {cfg['titulo']} - {data}"
        houve = C.git_publicar(msg, log)
        url = C.URL_BASE + cfg["url"]
        if houve:
            C.aguardar_publicacao(url, log)
        log("")
        log(f"Link publicado: {url}")
        if navegador:
            C.abrir_navegador(url, log)
    return resultado


# ---------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Uso: python atualizar.py <dashboard_id> [--sem-publicar] [--sem-navegador]")
        print("Dashboards: " + ", ".join(sorted(REGISTRO)))
        return 0

    dashboard_id = args[0]
    publicar = "--sem-publicar" not in args
    navegador = "--sem-navegador" not in args

    log = C.Log(dashboard_id)
    try:
        executar(dashboard_id, log, publicar=publicar, navegador=navegador)
        log.titulo("CONCLUIDO COM SUCESSO")
        return 0
    except C.FalhaAutomacao as e:
        log("")
        log("*" * 68)
        log("  FALHA — NADA FOI PUBLICADO")
        log("*" * 68)
        for linha in str(e).splitlines():
            log("  " + linha)
        return 1
    except KeyError as e:
        log("")
        log(f"  ERRO: {e}")
        return 1
    except Exception as e:  # erro inesperado
        log("")
        log("*" * 68)
        log("  ERRO INESPERADO — NADA FOI PUBLICADO")
        log("*" * 68)
        log(f"  {type(e).__name__}: {e}")
        return 1
    finally:
        caminho = log.salvar()
        print(f"\nLog salvo em: {caminho}")


if __name__ == "__main__":
    raise SystemExit(main())
