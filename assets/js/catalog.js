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
 */
window.PORTAL_CATALOG = {
  atualizacao: "2026-07-09",
  categorias: [
    {
      id: "acidentes", nome: "Acidentes Bombeiros UMO", cor: "#dc2626",
      grupo: "Segurança", versao: "v2.0", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "CBVJ — Corpo de Bombeiros Voluntários", tags: ["trânsito", "vítimas", "segurança"],
      descricao: "Ocorrências e atendimentos de acidentes de trânsito registrados pelo Corpo de Bombeiros (CBVJ).",
      href: "dashboards/acidentes/", bases: 1, atualizacao: "2026-07-09",
      keywords: ["acidentes", "bombeiros", "transito", "cbvj", "vitimas"],
      icone: '<path d="M10.5 2.5c.5 2 .5 3.5-1 5-2 2-2.5 4-1.5 6 .3-1.5 1-2.3 2-3-.3 2 .4 3.5 2 4.5 1.8 1.1 2.5 2.8 2 4.5-3 1-6-.5-7-3.5-1.2-3.5.5-6 1.5-7.5-1-.5-2-1.5-2-3 0-1.5 1.5-2.5 4-3z"/><path d="M9 21h9"/>',
      paineis: [{ nome: "Acidentes Bombeiros UMO", registros: 45011, atualizacao: "2026-07-08" }]
    },
    {
      id: "equipamentos", nome: "Equipamentos SEPUR", cor: "#16a34a",
      grupo: "Tecnologia", versao: "v2.0", responsavel: "SEPUR",
      fonte: "Controle Patrimonial de CPUs", tags: ["patrimônio", "TI", "equipamentos"],
      descricao: "Controle patrimonial de CPUs, kits e equipamentos de informática distribuídos pela SEPUR.",
      href: "dashboards/equipamentos/", bases: 1, atualizacao: "2026-07-09",
      keywords: ["equipamentos", "cpu", "patrimonio", "sepur", "informatica"],
      icone: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
      paineis: [{ nome: "Equipamentos SEPUR", registros: 76, atualizacao: "2026-07-08" }]
    },
    {
      id: "inventario", nome: "Inventário UMO", cor: "#7c3aed",
      grupo: "Tecnologia", versao: "v2.0", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "Inventário de CPUs por usuário", tags: ["TI", "ativos", "computadores"],
      descricao: "Levantamento e situação dos computadores e ativos de TI sob gestão da UMO.",
      href: "dashboards/inventario/", bases: 1, atualizacao: "2026-07-09",
      keywords: ["inventario", "computadores", "cpus", "ippuj", "ti", "ativos"],
      icone: '<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8M12 13v8"/>',
      paineis: [
        { nome: "Inventário · Computadores UMO", registros: 17, atualizacao: "2026-07-08" },
        { nome: "Inventário · CPUs IPPUJ", registros: 77, atualizacao: "2026-07-09" }
      ]
    },
    {
      id: "processos", nome: "Processos SEI UMO", cor: "#2563eb",
      grupo: "Administrativo", versao: "v2.1", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "SEI — Sistema Eletrônico de Informações", tags: ["processos", "tramitação"],
      descricao: "Tramitação, prazos e volume de processos do Sistema Eletrônico de Informações.",
      href: "dashboards/processos/", bases: 1, atualizacao: "2026-07-09",
      keywords: ["processos", "sei", "tramitacao", "prazos", "demandas"],
      icone: '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6M9 9h1"/>',
      paineis: [{ nome: "Processos SEI UMO", registros: 4090, atualizacao: "2026-07-09" }]
    },
    {
      id: "radares", nome: "Radares", cor: "#ea580c",
      grupo: "Mobilidade", versao: "v2.0", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "Radares de fiscalização municipal", tags: ["fiscalização", "velocidade"],
      descricao: "Monitoramento de velocidade e fluxo de veículos dos radares de fiscalização municipal.",
      href: "dashboards/radares/", bases: 1, atualizacao: null,
      keywords: ["radares", "velocidade", "fiscalizacao", "fluxo", "veiculos"],
      icone: '<circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/><path d="M12 12l7-4M4.5 8a9 9 0 0115 0M2 12a12 12 0 0120 0"/>',
      paineis: [{ nome: "Radares", registros: null, atualizacao: null, pendencia: "Base recebida; dashboard em processamento." }]
    },
    {
      id: "transporte", nome: "Transporte Público UMO", cor: "#0f766e",
      grupo: "Mobilidade", versao: "v2.0", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "Passebus / Consórcio de Transporte", tags: ["ônibus", "passageiros", "viagens"],
      descricao: "Viagens, passageiros transportados e desempenho da rede de transporte público.",
      href: "dashboards/transporte/", bases: 2, atualizacao: "2026-07-09",
      keywords: ["transporte", "onibus", "passageiros", "viagens", "mobilidade"],
      icone: '<rect x="3" y="6" width="18" height="11" rx="2"/><circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/><path d="M3 11h18"/>',
      paineis: [{ nome: "Transporte Público UMO", registros: 218454, atualizacao: "2026-07-08" }]
    },
    {
      id: "waze", nome: "Waze UMO", cor: "#d97706",
      grupo: "Mobilidade", versao: "v2.1", responsavel: "UMO — Unidade de Mobilidade",
      fonte: "Waze for Cities", tags: ["waze", "comunidade", "trânsito"],
      descricao: "Alertas, acidentes, alagamentos, buracos e ranqueamento reportados pela comunidade Waze.",
      href: "dashboards/waze/", bases: 5, atualizacao: "2026-07-09",
      keywords: ["waze", "buracos", "alagamentos", "alertas", "ranqueamento", "acidentes", "congestionamento"],
      icone: '<circle cx="12" cy="12" r="9"/><path d="M9 10c0-1 .8-2 3-2s3 1 3 2c0 1.5-3 2-3 4M12 17h.01"/>',
      paineis: [
        { nome: "Waze · Acidentes", registros: 4048, atualizacao: "2026-07-09" },
        { nome: "Waze · Alagamentos", registros: 5792, atualizacao: "2026-07-09" },
        { nome: "Waze · Alertas", registros: 1000, atualizacao: "2026-07-07", status: "updating", pendencia: "Aguardando exportação do histórico completo." },
        { nome: "Waze · Buracos na Via", registros: 155663, atualizacao: "2026-07-09" },
        { nome: "Waze · Ranqueamento", registros: null, registrosLabel: "15 meses", status: "online", atualizacao: "2026-07-08" }
      ]
    }
  ]
};

/* Metadados de governança do próprio Portal (não ligados a nenhum dashboard). */
window.PORTAL_META = {
  versao: "2.1.0",
  publicacao: "GitHub Pages",
  url: "https://pmj-sepud.github.io/portal-bi/",
  ultimaAtualizacao: "2026-07-09T13:06",
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
    objetivo: "Centralizar, padronizar e disponibilizar os indicadores de Business Intelligence da Prefeitura de Joinville em um único ambiente institucional, com dados auditados e apresentação consistente.",
    secretarias: [
      "SEPUR — Secretaria de Pesquisa e Planejamento Urbano",
      "UMO — Unidade de Mobilidade"
    ],
    origemDados: [
      "CBVJ — Corpo de Bombeiros Voluntários de Joinville",
      "Passebus / Consórcio de Transporte Público",
      "SEI — Sistema Eletrônico de Informações",
      "Waze for Cities",
      "Inventário e Controle Patrimonial (SEPUR)"
    ],
    periodicidade: "Atualização conforme o fechamento mensal de cada base; a regeneração dos dashboards é feita sob demanda pelo framework, sempre com auditoria de correspondência 1:1 com a planilha de origem.",
    arquitetura: "Site estático publicado no GitHub Pages. Home orientada por catálogo (dados dirigem cards, tabelas e métricas). Dashboards autossuficientes com dados embutidos.",
    framework: "Pipeline em Python (carregar_planilha → processador → exportador_html), config-driven: cada dashboard é um arquivo JSON. Auditoria automática Planilha → JSON → HTML.",
    designSystem: "Componentes visuais únicos derivados da referência Acidentes Bombeiros UMO; a identidade de cada categoria muda apenas pela cor institucional.",
    tecnologias: [
      "HTML5 · CSS3 · JavaScript (Vanilla)",
      "Python (pandas, openpyxl) — framework de geração",
      "GitHub Pages — hospedagem"
    ],
    equipe: "Secretaria de Pesquisa e Planejamento Urbano (SEPUR) · Unidade de Mobilidade (UMO)",
    contato: "SEPUR — Unidade de Mobilidade · Prefeitura Municipal de Joinville"
  }
};