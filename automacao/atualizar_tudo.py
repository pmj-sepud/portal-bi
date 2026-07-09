#!/usr/bin/env python3
"""
atualizar_tudo.py — Atualiza TODOS os dashboards do Portal BI em sequência.

Ordem oficial: Acidentes -> Equipamentos -> Inventário -> Processos
               -> Radares -> Transporte -> Waze

Ao final: UM único commit, UM único push, confirmação do GitHub Pages,
relatório consolidado e abertura automática da Home do Portal.

Se QUALQUER dashboard falhar na auditoria, a execução para e nada é publicado.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comum as C
from registro import ORDEM
from atualizar import executar


def main() -> int:
    navegador = "--sem-navegador" not in sys.argv
    publicar = "--sem-publicar" not in sys.argv

    log = C.Log("atualizar_tudo")
    resultados: list[dict] = []

    try:
        log.titulo("ATUALIZACAO COMPLETA DO PORTAL BI")
        C.checar_prerequisitos(log)

        for dashboard_id in ORDEM:
            r = executar(dashboard_id, log, publicar=False, navegador=False)
            resultados.append(r)

        # ---------------- Relatório consolidado ----------------
        log.titulo("RELATORIO CONSOLIDADO")
        total_geral = 0
        for r in resultados:
            if r["status"] == "ignorado":
                log(f"  [--] {r['titulo']:<32} sem dados/painel (ignorado)")
                continue
            if not r["paineis"]:
                log(f"  [ok] {r['titulo']:<32} republicado (sem gerador automatico)")
                continue
            for painel, total in r["paineis"].items():
                total_geral += total
                log(f"  [ok] {painel:<32} {total:>12,} registros".replace(",", "."))
        log("")
        log(f"  Total de registros processados: {total_geral:,}".replace(",", "."))
        log("  Auditoria: 100% de correspondencia em todos os dashboards gerados.")

        # ---------------- Publicação única ----------------
        if publicar:
            data = datetime.now().strftime("%d/%m/%Y %H:%M")
            msg = f"Atualizacao automatica - Portal BI (todos os dashboards) - {data}"
            houve = C.git_publicar(msg, log)
            if houve:
                C.aguardar_publicacao(C.URL_BASE, log)
            log("")
            log(f"Portal publicado: {C.URL_BASE}")
            if navegador:
                C.abrir_navegador(C.URL_BASE, log)

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
    except Exception as e:
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
