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
        "titulo": "Acidentes Bombeiros SEPUR",
        "tipo": "manual",
        "pasta": "Acidentes Bombeiros UMO",
        "html_gerado": "dashboard_acidentes.html",
        "portal": "dashboards/acidentes/index.html",
        "profundidade": "../../",
        "categoria": "acidentes",
        "url": "dashboards/acidentes/",
        "nota": ("Este painel nao possui gerador automatico: os dados ficam embutidos no "
                 "proprio HTML de origem ('dashboard_acidentes.html', const DATA). Para "
                 "atualizar, substitua esse HTML na pasta e rode este BAT: ele republica o "
                 "painel no Portal. Desde 28/09/2026 substitui o antigo Comparativo de vias "
                 "(gerar_dashboard_comparativo.py, que nao e mais usado)."),
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
        "titulo": "Transporte Público SEPUR",
        "tipo": "portal",                      # gerador escreve direto na pagina do Portal
        "pasta": "Transporte Publico UMO",
        "planilha": None,                      # le o 'Banco de Dados Dashboard' da propria pasta
        "gerador": "gerar_painel_planejamento.py",
        "portal": "dashboards/transporte/index.html",
        "categoria": "transporte",
        "painel": "Transporte Público SEPUR",
        "url": "dashboards/transporte/",
        "nota": ("Painel de Planejamento Operacional (desde 28/09/2026; o painel antigo "
                 "Bootstrap/ApexCharts foi desativado, copia em "
                 "portal_transporte_antigo_backup_20260928.html). O gerador reescreve o JSON "
                 "de painel_transporte_publico.html e remonta a pagina do Portal a partir dele."),
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
        "titulo": "Waze SEPUR",
        "tipo": "manual",
        "categoria": "waze",
        "url": "dashboards/waze/",
        # cada sub-painel: HTML de origem (dados embutidos) -> página do Portal.
        "subpaineis": [
            {"pasta": "Waze UMO/Acidentes Waze", "html_gerado": "Dashboard_Acidentes_Waze_Joinville.html",
             "portal": "dashboards/waze/acidentes/index.html", "profundidade": "../../../"},
            {"pasta": "Waze UMO/Alagamentos", "html_gerado": "Alagamentos_Joinville_dashboard.html",
             "portal": "dashboards/waze/alagamentos/index.html", "profundidade": "../../../"},
            {"pasta": "Waze UMO/Buracos na Via", "html_gerado": "Dashboard_Buracos_Waze_Joinville.html",
             "portal": "dashboards/waze/buracos/index.html", "profundidade": "../../../"},
        ],
        "nota": ("Desde 29/09/2026 Acidentes, Alagamentos e Buracos na Via nao possuem gerador "
                 "automatico: os dados ficam embutidos nos HTMLs de origem de cada pasta "
                 "(Dashboard_Acidentes_Waze_Joinville.html, Alagamentos_Joinville_dashboard.html, "
                 "Dashboard_Buracos_Waze_Joinville.html). Para atualizar, substitua esses HTMLs e "
                 "rode este BAT: ele republica os paineis no Portal. Substituem os antigos "
                 "comparativos do framework (gerar_comparativo.py, que nao e mais usado para eles). "
                 "'Alertas' e 'Ranqueamento' tem entradas proprias."),
    },
    "ranqueamento": {
        "titulo": "Waze · Ranqueamento",
        "tipo": "bespoke",
        "pasta": "Waze UMO/Ranqueamento Waze",
        "planilha": "Ranking Waze por mês/Ranking Waze Abril 2026.xlsx",  # so p/ log; o gerador le a pasta inteira
        "gerador": "gerar_dashboard_ranqueamento.py",
        "html_gerado": "dashboard_waze.html",
        "portal": "dashboards/waze/ranqueamento/mensal/index.html",
        "profundidade": "../../../../",
        "categoria": "waze",
        "painel": "Waze · Ranqueamento",
        "url": "dashboards/waze/ranqueamento/mensal/",
        "nota": ("Visual proprio (Bootstrap + ApexCharts, abas Visao Geral / Comparativo), "
                 "independente do template generico do framework. Le todos os arquivos de "
                 "'Ranking Waze por mês/*.xlsx' (nao um unico arquivo). "
                 "Opcao 'Ranking Mensal' da pagina de escolha dashboards/waze/ranqueamento/."),
    },
    "ranqueamento-congestionamentos": {
        "titulo": "Waze · Congestionamentos em Joinville",
        "tipo": "manual",
        "pasta": "Waze UMO/Ranqueamento Waze",
        "html_gerado": "congestionamentos-joinville.html",
        "portal": "dashboards/waze/ranqueamento/congestionamentos/index.html",
        "profundidade": "../../../../",
        "categoria": "waze",
        "url": "dashboards/waze/ranqueamento/congestionamentos/",
        "nota": ("Este painel nao possui gerador automatico: os dados sao mantidos no "
                 "proprio HTML de origem ('congestionamentos-joinville.html'). Edite o HTML "
                 "da pasta e rode este BAT: ele republica o painel no Portal (sem alterar "
                 "dados). Opcao 'Congestionamentos' da pagina de escolha "
                 "dashboards/waze/ranqueamento/."),
    },

    # ------------------------------------------------- SEM GERADOR AUTOMÁTICO
    "equipamentos": {
        "titulo": "Equipamentos SEPUR",
        "tipo": "manual",
        "pasta": "Equipamentos SEPUR",
        "html_gerado": "dashboard equipamentos.html",
        "portal": "dashboards/equipamentos/index.html",
        "profundidade": "../../",
        "categoria": "equipamentos",
        "url": "dashboards/equipamentos/",
        "nota": ("Este dashboard nao possui gerador automatico: os dados sao mantidos "
                 "no proprio HTML de origem. Edite o HTML da pasta e rode este BAT: "
                 "ele republica o painel no Portal (sem alterar dados). O HTML de origem "
                 "agora e um painel completo (design .viz-root), sem reskin institucional "
                 "aplicado por cima — o reskin antigo (equipamentos.css) tinha seletores "
                 "genericos (header/table/footer) com !important escritos pro layout escuro "
                 "anterior e conflitava com o novo design."),
    },
    "alertas": {
        "titulo": "Waze · Alertas",
        "tipo": "manual",
        "pasta": "Waze UMO/Alertas Waze",
        "html_gerado": "Dashboard Alertas.html",
        "portal": "dashboards/waze/alertas/index.html",
        "profundidade": "../../../",
        "categoria": "waze",
        "url": "dashboards/waze/alertas/",
        "nota": ("Este dashboard nao possui gerador automatico: os dados sao mantidos "
                 "no proprio HTML de origem ('Dashboard Alertas.html'). Edite o HTML da "
                 "pasta e rode este BAT: ele republica o painel no Portal (sem alterar "
                 "dados). Substitui o painel 'Alertas' do framework generico, que segue "
                 "bloqueado (planilha ainda parcial, ver 'waze')."),
    },
    "radares": {
        "titulo": "Relatório de Análise dos Radares",
        "tipo": "bespoke",
        "pasta": "Radares",
        "planilha": "2026",  # pasta do ano (so confere que existe); o gerador le todas as pastas <ano>/<MM>
        "gerador": "gerar_dashboard_radares.py",
        "html_gerado": "Dashboard_Radares.html",
        "portal": "dashboards/radares/index.html",
        "profundidade": "../../",
        "categoria": "radares",
        "painel": "Relatório de Análise dos Radares",
        "url": "dashboards/radares/",
        "nota": ("Le os 3 relatorios mensais (STKR007 classificacao, STKR009 velocidade, "
                 "STKR012 fluxo por hora) de cada pasta Radares/<ano>/<MM> e preenche o "
                 "modelo_dashboard_radares.html (nomes padronizados em cadastro_radares.json). "
                 "Pasta cujos relatorios sao de outro mes e ignorada. Para um mes novo, crie "
                 "a pasta <ano>/<MM> com os 3 arquivos STKR*.xls."),
    },
    "vida-no-transito": {
        "titulo": "Comitê Intersetorial Municipal de Prevenção de Lesões e Mortes no Trânsito",
        "tipo": "portal",                      # gerador escreve a pagina inteira do Portal
        "pasta": "Dados Projeto Vida no Trânsito",
        "planilha": "Acidentes Bombeiros Joinville - Dashboard.xlsx",
        "gerador": "gerar_dashboard_vida_transito.py",
        "portal": "dashboards/vida-no-transito/index.html",
        "categoria": "vida-no-transito",
        "painel": "Sinistros Fatais no Trânsito",
        "url": "dashboards/vida-no-transito/",
        "nota": ("Pagina mostra so o painel 'Obitos confirmados nas 3 bases' (SIM + "
                 "Bombeiros + Rede Hospitalar, 9 casos com acidente e obito dentro de 2025) "
                 "— dado fixo dentro do gerador (PAYLOAD3_JSON), nao recalculado "
                 "automaticamente; ver docstring do script para o que falta pra automatizar "
                 "essa parte."),
    },
    "intraempreendedorismo": {
        "titulo": "MVP SEPUR Programa de Intraempreendedorismo",
        "tipo": "manual",
        "pasta": "Programa de Intraempreendedorismo",
        "html_gerado": "MVP SEPUR Intraempreendedorismo.html",
        "portal": "dashboards/intraempreendedorismo/sepur/index.html",
        "profundidade": "../../../",
        "categoria": "intraempreendedorismo",
        "url": "dashboards/intraempreendedorismo/",
        "nota": ("Este painel nao possui gerador automatico: os dados sao mantidos "
                 "no proprio HTML de origem ('MVP SEPUR Intraempreendedorismo.html', "
                 "buscador de servicos da SEPUR). Edite o HTML da pasta e rode este "
                 "BAT: ele republica o painel no Portal (sem alterar dados). "
                 "Versao 1 do MVP; a pagina da categoria permite escolher a versao."),
    },
    "intraempreendedorismo-carta": {
        "titulo": "Carta de Serviços SEPUR · SAMA · SEFAZ",
        "tipo": "manual",
        "pasta": "Programa de Intraempreendedorismo",
        "html_gerado": "MVP intraempreendedorismo carta de servicoes SEPUR SAMA SEFAZ.html",
        "portal": "dashboards/intraempreendedorismo/carta-servicos/index.html",
        "profundidade": "../../../",
        "categoria": "intraempreendedorismo",
        "url": "dashboards/intraempreendedorismo/carta-servicos/",
        "nota": ("Versao 2 do MVP de Intraempreendedorismo (buscador SEPUR + SAMA + SEFAZ). "
                 "Sem gerador automatico: os dados ficam no proprio HTML de origem. Edite o "
                 "HTML da pasta e rode este BAT para republicar (sem alterar dados)."),
    },
}


def obter(dashboard_id: str) -> dict:
    if dashboard_id not in REGISTRO:
        validos = ", ".join(sorted(REGISTRO))
        raise KeyError(f"Dashboard desconhecido: '{dashboard_id}'.\nValidos: {validos}")
    return REGISTRO[dashboard_id]


# Ordem oficial usada pelo atualizar_tudo
ORDEM = ["acidentes", "equipamentos", "alertas", "intraempreendedorismo", "intraempreendedorismo-carta", "inventario", "processos", "radares", "ranqueamento", "ranqueamento-congestionamentos", "transporte", "waze"]
