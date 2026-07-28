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
        "tipo": "portal",                      # gerador escreve direto na página do Portal
        "pasta": "Acidentes Bombeiros UMO",
        "planilha": None,                      # detecta o .xlsx da própria pasta
        "gerador": "gerar_dashboard_comparativo.py",
        "portal": "dashboards/acidentes/index.html",
        "categoria": "acidentes",
        "painel": "Acidentes Bombeiros UMO",
        "url": "dashboards/acidentes/",
        "nota": ("Dashboard comparativo (vias A/B, análise de vítimas). O gerador le a "
                 "planilha e reescreve apenas o bloco de dados (data-payload) da propria "
                 "pagina do Portal; a interface nao e alterada."),
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
        # cada sub-painel: config -> página do Portal.
        # modo "comparativo": gerador oficial único = framework-dashboards/gerar_comparativo.py
        #   (escreve o data-payload direto na página; comparador Via A x B + mapa Waze).
        # modo "framework" (padrão): gerador config-driven clássico (dashboard_base).
        "subpaineis": [
            {"config": "acidentes_waze", "modo": "comparativo",
             "portal": "dashboards/waze/acidentes/index.html", "painel": "Waze · Acidentes"},
            {"config": "alagamentos", "modo": "comparativo",
             "portal": "dashboards/waze/alagamentos/index.html", "painel": "Waze · Alagamentos"},
            {"config": "buracos", "modo": "comparativo",
             "portal": "dashboards/waze/buracos/index.html", "painel": "Waze · Buracos na Via"},
        ],
        "nota": "O painel 'Alertas' está bloqueado (planilha ainda parcial) e não é regenerado. "
                "'Ranqueamento' saiu do framework generico e agora tem gerador proprio (ver 'ranqueamento').",
    },
    "ranqueamento": {
        "titulo": "Waze · Ranqueamento",
        "tipo": "bespoke",
        "pasta": "Waze UMO/Ranqueamento Waze",
        "planilha": "Ranking Waze por mês/Ranking Waze Abril 2026.xlsx",  # so p/ log; o gerador le a pasta inteira
        "gerador": "gerar_dashboard_ranqueamento.py",
        "html_gerado": "dashboard_waze.html",
        "portal": "dashboards/waze/ranqueamento/index.html",
        "profundidade": "../../../",
        "categoria": "waze",
        "painel": "Waze · Ranqueamento",
        "url": "dashboards/waze/ranqueamento/",
        "nota": ("Visual proprio (Bootstrap + ApexCharts, abas Visao Geral / Comparativo), "
                 "independente do template generico do framework. Le todos os arquivos de "
                 "'Ranking Waze por mês/*.xlsx' (nao um unico arquivo)."),
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
        "titulo": "Relatório de Análise dos Radares",
        "tipo": "bespoke",
        "pasta": "Radares",
        "planilha": None,  # gerador le os 3 relatorios STKR*.xls + geo da pasta inteira (nomes mudam a cada mes)
        "gerador": "gerar_dashboard_radares.py",
        "html_gerado": "dashboard_radares.html",
        "portal": "dashboards/radares/index.html",
        "profundidade": "../../",
        "categoria": "radares",
        "painel": "Relatório de Análise dos Radares",
        "url": "dashboards/radares/",
        "nota": ("Le 3 relatorios mensais (STKR007 classificacao, STKR009 velocidade, "
                 "STKR012 fluxo por hora) mais 'Banco de Dados - Radares.xlsx' (geo). "
                 "Ao trocar de mes, substitua os 3 arquivos STKR*.xls por uma exportacao "
                 "mais recente (mesmo padrao de nome) nesta pasta."),
    },
}


def obter(dashboard_id: str) -> dict:
    if dashboard_id not in REGISTRO:
        validos = ", ".join(sorted(REGISTRO))
        raise KeyError(f"Dashboard desconhecido: '{dashboard_id}'.\nValidos: {validos}")
    return REGISTRO[dashboard_id]


# Ordem oficial usada pelo atualizar_tudo
ORDEM = ["acidentes", "equipamentos", "inventario", "processos", "radares", "ranqueamento", "transporte", "waze"]
