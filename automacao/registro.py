"""
registro.py — Mapa oficial dos dashboards do Portal BI.

É a ÚNICA coisa que muda entre um BAT e outro. Cada entrada descreve, em
caminhos relativos, onde está a planilha, qual é o gerador oficial, para onde
o HTML vai no Portal e qual painel do Centro de Operações representa.

tipo:
  "framework" — gerado pelo Framework BI (config-driven, auditoria embutida)
  "bespoke"   — gerado pelo script oficial da própria pasta
  "manual"    — dados mantidos à mão (sem gerador) — nada a gerar
  "placeholder" — ainda não possui dashboard/dados
"""

REGISTRO: dict[str, dict] = {
    # ------------------------------------------------------------- BESPOKE
    "acidentes": {
        "titulo": "Acidentes Bombeiros UMO",
        "tipo": "bespoke",
        "pasta": "Acidentes Bombeiros UMO",
        "planilha": None,                      # detecta o .xlsx da própria pasta
        "gerador": "gerar_dashboard.py",
        "html_gerado": "dashboard_acidentes_joinville.html",
        "portal": "dashboards/acidentes/index.html",
        "profundidade": "../../",
        "reskin": "acidentes.css",
        "categoria": "acidentes",
        "painel": "Acidentes Bombeiros UMO",
        "url": "dashboards/acidentes/",
    },
    "processos": {
        "titulo": "Processos SEI UMO",
        "tipo": "bespoke",
        "pasta": "Processos SEI UMO",
        "planilha": "SEPUR.UMO.G_pl_bad_Dashboard SEI 2021_ATUAL.xlsx",
        "gerador": "atualizar_dashboard.py",
        "html_gerado": "dashboard_sei_umo.html",
        "portal": "dashboards/processos/index.html",
        "profundidade": "../../",
        "reskin": "processos.css",
        "categoria": "processos",
        "painel": "Processos SEI UMO",
        "url": "dashboards/processos/",
    },
    "transporte": {
        "titulo": "Transporte Público UMO",
        "tipo": "bespoke",
        "pasta": "Transporte Publico UMO",
        "planilha": None,
        "gerador": "gerar_dashboard_transporte.py",
        "html_gerado": "dashboard_transporte_joinville.html",
        "portal": "dashboards/transporte/index.html",
        "profundidade": "../../",
        "reskin": "transporte.css",
        "categoria": "transporte",
        "painel": "Transporte Público UMO",
        "url": "dashboards/transporte/",
    },
    "inventario": {
        "titulo": "Inventário UMO (CPUs IPPUJ)",
        "tipo": "bespoke",
        "pasta": "Inventario UMO",
        "planilha": None,
        "gerador": "gerar_dashboard.py",
        "html_gerado": "Dashboard_CPUs_IPPUJ.html",
        "portal": "dashboards/inventario/ippuj/index.html",
        "profundidade": "../../../",
        "reskin": "inventario_ippuj.css",
        "categoria": "inventario",
        "painel": "Inventário · CPUs IPPUJ",
        "url": "dashboards/inventario/ippuj/",
        "nota": "O painel 'Computadores UMO' desta categoria é mantido manualmente (sem gerador).",
    },

    # ----------------------------------------------------------- FRAMEWORK
    "waze": {
        "titulo": "Waze UMO",
        "tipo": "framework",
        "categoria": "waze",
        "url": "dashboards/waze/",
        # cada sub-painel: config do framework -> saída -> página do Portal
        "subpaineis": [
            {"config": "acidentes_waze", "html_gerado": "dashboard_acidentes.html",
             "portal": "dashboards/waze/acidentes/index.html", "profundidade": "../../../",
             "painel": "Waze · Acidentes"},
            {"config": "alagamentos", "html_gerado": "alagamentos_dashboard.html",
             "portal": "dashboards/waze/alagamentos/index.html", "profundidade": "../../../",
             "painel": "Waze · Alagamentos"},
            {"config": "buracos", "html_gerado": "buracos_dashboard.html",
             "portal": "dashboards/waze/buracos/index.html", "profundidade": "../../../",
             "painel": "Waze · Buracos na Via"},
            {"config": "ranqueamento", "html_gerado": "dashboard_waze.html",
             "portal": "dashboards/waze/ranqueamento/index.html", "profundidade": "../../../",
             "painel": "Waze · Ranqueamento"},
        ],
        "nota": "O painel 'Alertas' está bloqueado (planilha ainda parcial) e não é regenerado.",
    },

    # ------------------------------------------------- SEM GERADOR AUTOMÁTICO
    "equipamentos": {
        "titulo": "Equipamentos SEPUR",
        "tipo": "manual",
        "pasta": "Equipamentos SEPUR",
        "html_gerado": "dashboard_cpus_2026.html",
        "portal": "dashboards/equipamentos/index.html",
        "profundidade": "../../",
        "reskin": "equipamentos.css",
        "categoria": "equipamentos",
        "url": "dashboards/equipamentos/",
        "nota": ("Este dashboard nao possui gerador automatico: os dados sao mantidos "
                 "no proprio HTML de origem. Edite o HTML da pasta e rode este BAT: "
                 "ele republica o painel no Portal (sem alterar dados)."),
    },
    "radares": {
        "titulo": "Radares",
        "tipo": "placeholder",
        "pasta": "Radares",
        "categoria": "radares",
        "url": "dashboards/radares/",
        "nota": ("Ainda nao existe dashboard de Radares (apenas a base). "
                 "Quando o painel for criado, cadastre-o aqui no registro."),
    },
}


def obter(dashboard_id: str) -> dict:
    if dashboard_id not in REGISTRO:
        validos = ", ".join(sorted(REGISTRO))
        raise KeyError(f"Dashboard desconhecido: '{dashboard_id}'.\nValidos: {validos}")
    return REGISTRO[dashboard_id]


# Ordem oficial usada pelo atualizar_tudo
ORDEM = ["acidentes", "equipamentos", "inventario", "processos", "radares", "transporte", "waze"]
