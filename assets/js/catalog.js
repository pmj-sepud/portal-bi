/**
 * catalog.js — Catálogo institucional do Portal BI (fonte única de dados).
 *
 * Toda a home (cards, busca, favoritos, contadores, badges de status) é
 * renderizada a partir deste catálogo. Para adicionar um dashboard ao portal,
 * basta acrescentar um objeto aqui — nenhuma marcação HTML precisa mudar.
 *
 * status: 'ok' (🟢 Atualizado) | 'updating' (🟡 Atualizando) | 'pending' (🔴 Dados pendentes)
 * A regra é automática em portal.js: sem registros => pendente; flag updating => atualizando.
 */
window.PORTAL_CATALOG = {
  atualizacao: "2026-07-08",
  versao: "2.0.0",
  categorias: [
    {
      id: "acidentes",
      nome: "Acidentes Bombeiros UMO",
      cor: "#dc2626",
      descricao: "Ocorrências e atendimentos de acidentes de trânsito registrados pelo Corpo de Bombeiros (CBVJ).",
      href: "dashboards/acidentes/",
      registros: 45011,
      bases: 1,
      atualizacao: "2026-07-08",
      updating: false,
      keywords: ["acidentes", "bombeiros", "transito", "cbvj", "vitimas"],
      icone: '<path d="M10.5 2.5c.5 2 .5 3.5-1 5-2 2-2.5 4-1.5 6 .3-1.5 1-2.3 2-3-.3 2 .4 3.5 2 4.5 1.8 1.1 2.5 2.8 2 4.5-3 1-6-.5-7-3.5-1.2-3.5.5-6 1.5-7.5-1-.5-2-1.5-2-3 0-1.5 1.5-2.5 4-3z"/><path d="M9 21h9"/>'
    },
    {
      id: "equipamentos",
      nome: "Equipamentos SEPUR",
      cor: "#16a34a",
      descricao: "Controle patrimonial de CPUs, kits e equipamentos de informática distribuídos pela SEPUR.",
      href: "dashboards/equipamentos/",
      registros: 76,
      bases: 1,
      atualizacao: "2026-07-08",
      updating: false,
      keywords: ["equipamentos", "cpu", "patrimonio", "sepur", "informatica"],
      icone: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>'
    },
    {
      id: "inventario",
      nome: "Inventário UMO",
      cor: "#7c3aed",
      descricao: "Levantamento e situação dos computadores e ativos de TI sob gestão da UMO.",
      href: "dashboards/inventario/",
      registros: 94,
      bases: 1,
      atualizacao: "2026-07-08",
      updating: false,
      subpaineis: ["Computadores UMO 2026", "CPUs IPPUJ"],
      keywords: ["inventario", "computadores", "cpus", "ippuj", "ti", "ativos"],
      icone: '<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8M12 13v8"/>'
    },
    {
      id: "processos",
      nome: "Processos SEI UMO",
      cor: "#2563eb",
      descricao: "Tramitação, prazos e volume de processos do Sistema Eletrônico de Informações.",
      href: "dashboards/processos/",
      registros: 4086,
      bases: 1,
      atualizacao: "2026-07-08",
      updating: false,
      keywords: ["processos", "sei", "tramitacao", "prazos", "demandas"],
      icone: '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6M9 9h1"/>'
    },
    {
      id: "radares",
      nome: "Radares",
      cor: "#ea580c",
      descricao: "Monitoramento de velocidade e fluxo de veículos dos radares de fiscalização municipal.",
      href: "dashboards/radares/",
      registros: null,
      bases: 1,
      atualizacao: null,
      updating: false,
      keywords: ["radares", "velocidade", "fiscalizacao", "fluxo", "veiculos"],
      icone: '<circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/><path d="M12 12l7-4M4.5 8a9 9 0 0115 0M2 12a12 12 0 0120 0"/>'
    },
    {
      id: "transporte",
      nome: "Transporte Público UMO",
      cor: "#0f766e",
      descricao: "Viagens, passageiros transportados e desempenho da rede de transporte público.",
      href: "dashboards/transporte/",
      registros: 218454,
      bases: 2,
      atualizacao: "2026-07-08",
      updating: false,
      keywords: ["transporte", "onibus", "passageiros", "viagens", "mobilidade"],
      icone: '<rect x="3" y="6" width="18" height="11" rx="2"/><circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/><path d="M3 11h18"/>'
    },
    {
      id: "waze",
      nome: "Waze UMO",
      cor: "#d97706",
      descricao: "Alertas, acidentes, alagamentos, buracos e ranqueamento reportados pela comunidade Waze.",
      href: "dashboards/waze/",
      registros: 166434,
      bases: 5,
      atualizacao: "2026-07-08",
      updating: true,
      subpaineis: ["Acidentes Waze", "Alagamentos", "Alertas Waze", "Buracos na Via", "Ranqueamento"],
      keywords: ["waze", "buracos", "alagamentos", "alertas", "ranqueamento", "acidentes", "congestionamento"],
      icone: '<circle cx="12" cy="12" r="9"/><path d="M9 10c0-1 .8-2 3-2s3 1 3 2c0 1.5-3 2-3 4M12 17h.01"/>'
    }
  ]
};
