/**
 * catalog.js — Catálogo institucional do Portal BI (fonte única de dados).
 *
 * Toda a home (cards, busca, favoritos, contadores, Centro de Operações,
 * tabela de monitoramento, página Sobre) é gerada a partir daqui. Para incluir
 * um módulo, basta acrescentar um objeto em `categorias` — nenhuma marcação
 * HTML precisa mudar.
 *
 * Cada categoria pode conter vários `paineis` (dashboards). O status é
 * automático (portal.js): sem registros => 🟠 Atenção; painel parcial
 * (status:"updating") => 🟡 Atualizando; caso contrário => 🟢 Online.
 *
 * `oculto: true` esconde a categoria do portal e da TV sem apagar o cadastro.
 */
window.PORTAL_CATALOG = {
  atualizacao: "2026-10-01",
  categorias: [
    {
      id: "acidentes", nome: "Acidentes Bombeiros SEPUR", cor: "#b42318",
      grupo: "Segurança", versao: "v2.0", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "CBVJ — Corpo de Bombeiros Voluntários", tags: ["trânsito", "vítimas", "segurança"],
      descricao: "Acidentes de trânsito atendidos pelos Bombeiros (CBVJ) de 2016 a ago/2026: tendência, dia e hora, tipos de colisão, ruas críticas, letalidade e perfil das vítimas.",
      href: "dashboards/acidentes/", bases: 1, atualizacao: "2026-10-01",
      keywords: ["acidentes", "bombeiros", "transito", "cbvj", "vitimas"],
      icone: '<image href="assets/images/icones/acidentes.png" x="0" y="0" width="24" height="24"/>',
      paineis: [{ nome: "Acidentes Bombeiros SEPUR", registros: 38732, atualizacao: "2026-09-28" }]
    },
    {
      id: "equipamentos", nome: "Equipamentos SEPUR", cor: "#475467",
      grupo: "Tecnologia", versao: "v2.0", responsavel: "Secretaria de Pesquisa e Planejamento Urbano – SEPUR",
      fonte: "Controle Patrimonial de CPUs", tags: ["patrimônio", "TI", "equipamentos"],
      descricao: "Controle patrimonial de CPUs, kits e equipamentos de informática distribuídos pela Secretaria de Pesquisa e Planejamento Urbano – SEPUR.",
      href: "dashboards/equipamentos/", bases: 1, atualizacao: "2026-09-24",
      keywords: ["equipamentos", "cpu", "patrimonio", "sepur", "informatica"],
      icone: '<image href="assets/images/icones/equipamentos.png" x="0" y="0" width="24" height="24"/>',
      paineis: [{ nome: "Equipamentos SEPUR", registros: 77, atualizacao: "2026-09-09" }]
    },
    {
      id: "processos", oculto: true, nome: "Processos SEI UMO", cor: "#344e86",
      grupo: "Administrativo", versao: "v2.1", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "SEI — Sistema Eletrônico de Informações", tags: ["processos", "tramitação"],
      descricao: "Tramitação, prazos e volume de processos do Sistema Eletrônico de Informações.",
      href: "dashboards/processos/", bases: 1, atualizacao: "2026-10-01",
      keywords: ["processos", "sei", "tramitacao", "prazos", "demandas"],
      icone: '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6M9 9h1"/>',
      paineis: [{ nome: "Processos SEI UMO", registros: 5834, atualizacao: "2026-10-01" }]
    },
    {
      id: "radares", nome: "Relatório de Análise dos Radares", cor: "#3e5c8a",
      grupo: "Mobilidade", versao: "v2.0", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "Radares de fiscalização municipal", tags: ["fiscalização", "velocidade"],
      descricao: "Monitoramento de velocidade e fluxo de veículos dos radares de fiscalização municipal.",
      href: "dashboards/radares/", bases: 1, atualizacao: "2026-10-01",
      keywords: ["radares", "velocidade", "fiscalizacao", "fluxo", "veiculos"],
      icone: '<image href="assets/images/icones/radares.png" x="0" y="0" width="24" height="24"/>',
      paineis: [{ nome: "Relatório de Análise dos Radares", registros: 2211, atualizacao: "2026-10-01" }]
    },
    {
      id: "transporte", nome: "Transporte Público SEPUR", cor: "#1d5fa8",
      grupo: "Mobilidade", versao: "v2.0", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "Passebus / Consórcio de Transporte", tags: ["ônibus", "passageiros", "viagens"],
      descricao: "Viagens, passageiros transportados e desempenho da rede de transporte público.",
      href: "dashboards/transporte/", bases: 2, atualizacao: "2026-10-01",
      keywords: ["transporte", "onibus", "passageiros", "viagens", "mobilidade"],
      icone: '<image href="assets/images/icones/transporte.png" x="0" y="0" width="24" height="24"/>',
      paineis: [{ nome: "Transporte Público SEPUR", registros: 196957, atualizacao: "2026-10-01" }]
    },
    {
      id: "waze", nome: "Waze SEPUR", cor: "#0e7490",
      grupo: "Mobilidade", versao: "v2.1", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "Waze for Cities", tags: ["waze", "comunidade", "trânsito"],
      descricao: "Alertas, acidentes, alagamentos, buracos, ranqueamento e congestionamentos reportados pela comunidade Waze.",
      href: "dashboards/waze/", bases: 6, atualizacao: "2026-10-01",
      keywords: ["waze", "buracos", "alagamentos", "alertas", "ranqueamento", "acidentes", "congestionamento", "congestionamentos", "lentidao", "transito"],
      icone: '<image href="assets/images/icones/waze.png" x="0" y="0" width="24" height="24"/>',
      paineis: [
        { nome: "Waze · Acidentes", registros: 6774, atualizacao: "2026-09-29" },
        { nome: "Waze · Alagamentos", registros: 270, atualizacao: "2026-09-29" },
        { nome: "Waze · Alertas", registros: 458, atualizacao: "2026-09-29" },
        { nome: "Waze · Buracos na Via", registros: 626, atualizacao: "2026-09-29" },
        { nome: "Waze · Ranqueamento", registros: null, registrosLabel: "16 meses", status: "online", atualizacao: "2026-09-24" },
        { nome: "Waze · Congestionamentos", registros: null, status: "online", atualizacao: "2026-09-27" }
      ]
    },
    {
      id: "vida-no-transito", nome: "Óbitos por Acidentes de Trânsito — 2025", cor: "#7a1f2b",
      grupo: "Segurança", versao: "v1.0", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "CBVJ (APH) e SIM/DATASUS", tags: ["trânsito", "óbitos", "vítimas fatais"],
      descricao: "Cruzamento entre atendimentos pré-hospitalares dos Bombeiros e óbitos por acidente de transporte (SIM/DATASUS) em 2025.",
      href: "dashboards/vida-no-transito/", bases: 2, atualizacao: "2026-09-17",
      keywords: ["vida no transito", "obitos", "sinistros fatais", "sim", "datasus", "bombeiros", "aph", "comite intersetorial", "pvt"],
      icone: '<path d="M12 21s-7-4.35-9.5-9A5.5 5.5 0 0112 5.5 5.5 5.5 0 0121.5 12c-2.5 4.65-9.5 9-9.5 9z"/>',
      paineis: [{ nome: "Sinistros Fatais no Trânsito", registros: 9, atualizacao: "2026-09-17" }]
    },
    {
      id: "rede-cicloviaria", nome: "Rede Cicloviária de Joinville", cor: "#2f7d5b",
      grupo: "Mobilidade", versao: "v1.0", responsavel: "Secretaria de Pesquisa e Planejamento Urbano – SEPUR",
      fonte: "PLANMOB, Cidade em Dados, Detran e UPD-Geo", tags: ["bicicleta", "ciclovia", "mobilidade ativa"],
      descricao: "Evolução da extensão da rede cicloviária de Joinville, com ciclofaixas, ciclovias, ciclorrotas e vias compartilhadas. Agora com filtros por ano e por tipo de via.",
      href: "dashboards/rede-cicloviaria/", bases: 1, atualizacao: "2026-09-09",
      keywords: ["rede cicloviaria", "cicloviaria", "ciclovia", "ciclofaixa", "ciclorrota", "bicicleta", "planmob", "mobilidade ativa"],
      icone: '<image href="assets/images/icones/rede-cicloviaria.png" x="0" y="0" width="24" height="24"/>',
      paineis: [{ nome: "Rede Cicloviária de Joinville", registros: null, status: "online", atualizacao: "2026-09-09" }]
    },
    {
      id: "intraempreendedorismo", nome: "MVP: Onde eu resolvo?", cor: "#5b4bb7",
      grupo: "Administrativo", versao: "v1.0", responsavel: "Secretaria de Pesquisa e Planejamento Urbano – SEPUR",
      fonte: "Carta de Serviços da SEPUR, SAMA e SEFAZ", tags: ["sepur", "sama", "sefaz", "serviços", "buscador"],
      descricao: "MVP: um modelo de linguagem treinado diretamente com a Carta de Serviços e dados do portal da prefeitura. Em linguagem natural, o munícipe descreve seu problema e a IA identifica instantaneamente a necessidade exata e encaminha o solicitante para a secretaria ou setor responsável, informando inclusive pré requisitos de documentação. Eliminamos o erro de transbordo na entrada, reduzimos os atendimentos dessa natureza e garantimos eficiência real para a gestão pública.",
      href: "dashboards/intraempreendedorismo/", bases: 3, atualizacao: "2026-09-30",
      keywords: ["intraempreendedorismo", "sepur", "buscador", "servicos", "carta de servicos", "outorga", "vizinhanca", "plano viario", "sama", "sefaz", "meio ambiente", "fazenda", "onde eu resolvo", "urbana", "assistente"],
      icone: '<image href="assets/images/icones/intraempreendedorismo.png" x="0" y="0" width="24" height="24"/>',
      paineis: [
        // ocultos: { nome: "Buscador SEPUR", ... }, { nome: "Carta de Serviços SEPUR · SAMA · SEFAZ", ... },
        // ocultos: "MVP Onde eu resolvo?" (busca) e Versões 1 e 2 do chat
        { nome: "MVP Onde eu resolvo?", registros: null, status: "online", atualizacao: "2026-09-30" }
      ]
    }
  ]
};

/* Metadados de governança do próprio Portal (não ligados a nenhum dashboard). */
window.PORTAL_META = {
  versao: "2.1.0",
  publicacao: "GitHub Pages",
  url: "https://pmj-sepud.github.io/portal-bi/",
  ultimaAtualizacao: "2026-10-01T10:31",
  auditoria: "100% aprovada",
  framework: 1,
  designSystem: 1,
  changelog: [
    {
      versao: "2.1.0", data: "2026-07-09", atual: true,
      itens: [
        "Atualização de dados: Processos SEI (4.090), Waze · Acidentes (4.048) e Waze · Buracos (155.663) — período até 08/07/2026",
        "Auditoria de correspondência 100% (planilha → framework → dashboard)"
      ]
    },
    {
      versao: "2.0.0", data: "2026-07-08",
      itens: [
        "Portal redesenhado como app-shell corporativo",
        "Design System institucional único criado",
        "Framework unificado de geração de dashboards",
        "Dark mode com persistência",
        "Auditoria automática de dados (100%)",
        "Centro de Operações e Governança na home"
      ]
    },
    {
      versao: "1.0.0", data: "2026-07-08",
      itens: [
        "Portal inicial com 7 categorias",
        "Dashboards integrados ao portal",
        "Publicação no GitHub Pages"
      ]
    }
  ],
  sobre: {
    objetivo: "Centralizar, padronizar e disponibilizar os indicadores de Business Intelligence de Joinville/SC em um único ambiente institucional, com dados auditados e apresentação consistente.",
    secretarias: [
      "Secretaria de Pesquisa e Planejamento Urbano – SEPUR",
      "UMO — Unidade de Mobilidade"
    ],
    origemDados: [
      "CBVJ — Corpo de Bombeiros Voluntários de Joinville",
      "Passebus / Consórcio de Transporte Público",
      "SEI — Sistema Eletrônico de Informações",
      "Waze for Cities",
      "Inventário e Controle Patrimonial (Secretaria de Pesquisa e Planejamento Urbano – SEPUR)"
    ],
    periodicidade: "Atualização conforme o fechamento mensal de cada base; a regeneração dos dashboards é feita sob demanda pelo framework, sempre com auditoria de correspondência 1:1 com a planilha de origem.",
    arquitetura: "Site estático publicado no GitHub Pages. Home orientada por catálogo (dados dirigem cards, tabelas e métricas). Dashboards autossuficientes com dados embutidos.",
    framework: "Pipeline em Python (carregar_planilha → processador → exportador_html), config-driven: cada dashboard é um arquivo JSON. Auditoria automática Planilha → JSON → HTML.",
    designSystem: "Componentes visuais únicos derivados da referência Acidentes Bombeiros SEPUR; a identidade de cada categoria muda apenas pela cor institucional.",
    tecnologias: [
      "HTML5 · CSS3 · JavaScript (Vanilla)",
      "Python (pandas, openpyxl) — framework de geração",
      "GitHub Pages — hospedagem"
    ],
    equipe: "Secretaria de Pesquisa e Planejamento Urbano – SEPUR · Unidade de Mobilidade (UMO)",
    contato: "Secretaria de Pesquisa e Planejamento Urbano – SEPUR · Unidade de Mobilidade · Joinville/SC"
  }
};