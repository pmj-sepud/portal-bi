/**
 * enhance-equipamentos.js — Camada visual ADITIVA do dashboard Equipamentos SEPUR.
 *
 * Apenas apresentação: NÃO altera dados, filtros, busca, KPIs originais nem a
 * tabela. Lê o DOM já renderizado pelo dashboard e acrescenta:
 *   • badge de categoria no cabeçalho;
 *   • linha de indicadores (cards KPI padrão) sincronizada com o filtro atual;
 *   • métricas por seção (CPUs / usuários) e ícone no cabeçalho de cada setor.
 * Reage a cada re-render via MutationObserver (idempotente).
 */
(function () {
  "use strict";

  function nf(n) { return Number(n).toLocaleString("pt-BR"); }

  /* Badge de categoria no header (uma vez). */
  function addBadge() {
    var hl = document.querySelector("header .header-left");
    if (!hl || hl.querySelector(".eq-badge")) return;
    var b = document.createElement("span");
    b.className = "eq-badge";
    b.textContent = "Equipamentos · SEPUR";
    hl.appendChild(b);
  }

  /* Linha de indicadores (cards KPI) — inserida uma vez após o header. */
  var KPIS = [
    { id: "usuarios", ic: "👥", k: "Usuários" },
    { id: "cpus", ic: "🖥️", k: "CPUs" },
    { id: "setores", ic: "🏢", k: "Setores" },
    { id: "transfer", ic: "↔️", k: "Transferências" },
    { id: "vagos", ic: "🪑", k: "PCs vagos" }
  ];
  function ensureKpiRow() {
    if (document.getElementById("eqKpis")) return;
    var header = document.querySelector("header");
    if (!header) return;
    var label = document.createElement("div");
    label.className = "eq-section-label";
    label.textContent = "Indicadores gerais";
    var row = document.createElement("div");
    row.className = "eq-kpis";
    row.id = "eqKpis";
    row.innerHTML = KPIS.map(function (m) {
      return '<div class="eq-kpi"><div class="ic">' + m.ic + '</div><div class="tx"><div class="k">' + m.k +
        '</div><div class="v" id="eqk-' + m.id + '">—</div></div></div>';
    }).join("");
    header.insertAdjacentElement("afterend", label);
    label.insertAdjacentElement("afterend", row);
  }

  function setKpi(id, v) { var e = document.getElementById("eqk-" + id); if (e) e.textContent = nf(v); }

  /* Atualiza indicadores + métricas por seção a partir do DOM renderizado. */
  function refresh() {
    var main = document.getElementById("mainContent");
    if (!main) return;

    var totalRows = main.querySelectorAll("tbody tr").length;
    var totalVagos = main.querySelectorAll(".badge-vago").length;
    var totalTransfer = main.querySelectorAll(".badge-transfer").length;
    var secoes = main.querySelectorAll(".section");

    setKpi("usuarios", Math.max(0, totalRows - totalVagos));
    setKpi("cpus", totalRows);
    setKpi("setores", secoes.length);
    setKpi("transfer", totalTransfer);
    setKpi("vagos", totalVagos);

    secoes.forEach(function (sec) {
      var rows = sec.querySelectorAll("tbody tr").length;
      var vagos = sec.querySelectorAll(".badge-vago").length;
      var head = sec.querySelector(".section-header");
      if (!head) return;

      // Ícone no "dot" do setor (mantém a cor institucional inline do setor).
      var dot = head.querySelector(".section-dot");
      if (dot && dot.textContent !== "💻") dot.textContent = "💻";

      // Métricas da seção (CPUs / usuários) — recriadas a cada render.
      var m = head.querySelector(".section-metrics");
      if (!m) { m = document.createElement("div"); m.className = "section-metrics"; head.appendChild(m); }
      m.innerHTML =
        '<span class="section-metric">🖥️ <b>' + nf(rows) + "</b> CPUs</span>" +
        '<span class="section-metric">👤 <b>' + nf(Math.max(0, rows - vagos)) + "</b> usuários</span>";
    });
  }

  function boot() {
    addBadge();
    ensureKpiRow();
    refresh();
    var main = document.getElementById("mainContent");
    if (main && window.MutationObserver) {
      var t;
      new MutationObserver(function () { clearTimeout(t); t = setTimeout(refresh, 40); })
        .observe(main, { childList: true, subtree: true });
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
