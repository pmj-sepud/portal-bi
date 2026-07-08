#!/usr/bin/env python3
"""
gerar.py — Ponto de entrada do Framework de Dashboards.

Uso:
    python gerar.py                      # gera todos os dashboards ativos
    python gerar.py alagamentos buracos  # gera apenas os indicados

Cada dashboard é definido por um arquivo em config/<nome>.json. O pipeline
completo (dados → processamento → renderização → auditoria) roda para cada um.
Configs marcadas como "bloqueado" (ex.: alertas) são puladas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geradores import dashboard_base

# Dashboards ativos por padrão (Alertas fica de fora: fonte incompleta).
PADRAO = ["alagamentos", "buracos", "ranqueamento", "acidentes_waze"]


def main():
    nomes = sys.argv[1:] or PADRAO
    resultados = {}
    for nome in nomes:
        resultados[nome] = dashboard_base.gerar(nome)

    print("\n" + "=" * 60)
    print("RESUMO DA GERAÇÃO")
    print("=" * 60)
    for nome, r in resultados.items():
        if r.get("bloqueado"):
            print(f"  • {nome:14s} BLOQUEADO (não regenerado)")
        else:
            aud = r.get("auditoria", {})
            status = "100% OK" if aud.get("ok") else "DIVERGENTE"
            print(f"  • {nome:14s} {status}")


if __name__ == "__main__":
    main()
