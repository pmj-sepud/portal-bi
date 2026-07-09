/**
 * portal.js — Motor da home do Portal BI (Centro de Operações e Governança).
 * Renderiza, a partir do catálogo (catalog.js) e de PORTAL_META:
 *   • Visão Geral — cards com busca em tempo real, favoritos, filtro por categoria;
 *   • Operações  — saúde do sistema, métricas do portal, tabela de monitoramento;
 *   • Sobre      — informações institucionais e histórico de versões.
 * Sem dependências externas. Tudo é dirigido por dados (nada fixo no HTML).
 */
(function () {
  "use strict";

  var CAT = window.PORTAL_CATALOG || { categorias: [] };
  var META = window.PORTAL_META || {};
  var ITENS = CAT.categorias;
  var FAV_KEY = "portalbi:favoritos";
  var THEME_KEY = "portalbi:tema";

  /* ---------------- utilidades ---------------- */
  var WD = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"];
  var MO = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  function pad(n) { return String(n).padStart(2, "0"); }
  function nf(n) { return (n == null) ? "—" : n.toLocaleString("pt-BR"); }
  function fmtData(iso) { if (!iso) return "—"; var d = new Date(iso.slice(0, 10) + "T00:00:00"); return pad(d.getDate()) + "/" + pad(d.getMonth() + 1) + "/" + d.getFullYear(); }
  function fmtDataHora(iso) { if (!iso) return "—"; var d = new Date(iso); return pad(d.getDate()) + "/" + pad(d.getMonth() + 1) + "/" + d.getFullYear() + " " + pad(d.getHours()) + ":" + pad(d.getMinutes()); }
  function semAcento(s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  function el(id) { return document.getElementById(id); }
  function setText(id, v) { var e = el(id); if (e) e.textContent = v; }

  /* ---------------- status (4 estados) ---------------- */
  var LABEL = { online: "Online", updating: "Atualizando", atencao: "Atenção", offline: "Offline" };
  var RANK = { online: 0, updating: 1, atencao: 2, offline: 3 };
  function statusPainel(p) { return p.status || (p.registros == null ? "atencao" : "online"); }
  function statusCategoria(c) {
    return (c.paineis || []).reduce(function (acc, p) {
      var s = statusPainel(p); return RANK[s] > RANK[acc] ? s : acc;
    }, "online");
  }
  function badge(cls) { return '<span class="badge ' + cls + '">' + LABEL[cls] + "</span>"; }

  /* ---------------- derivações do catálogo ---------------- */
  function enriquecer() {
    ITENS.forEach(function (c) {
      var pans = c.paineis || [];
      c._registros = pans.reduce(function (s, p) { return s + (typeof p.registros === "number" ? p.registros : 0); }, 0);
      c._status = statusCategoria(c);
      c._subs = pans.length > 1 ? pans.map(function (p) { return p.nome.replace(/^.*·\s*/, ""); }) : [];
      c._temValor = pans.some(function (p) { return p.registros != null; });
    });
  }
  function todosPaineis() {
    var arr = [];
    ITENS.forEach(function (c) { (c.paineis || []).forEach(function (p) { arr.push({ p: p, c: c }); }); });
    return arr;
  }
  function metrics() {
    var pans = todosPaineis();
    var ativos = pans.filter(function (x) { return statusPainel(x.p) !== "atencao"; }).length;
    var registros = ITENS.reduce(function (s, c) { return s + c._registros; }, 0);
    var bases = ITENS.reduce(function (s, c) { return s + (c.bases || 0); }, 0);
    return { paineis: pans.length, ativos: ativos, categorias: ITENS.length, registros: registros, bases: bases };
  }

  /* ---------------- favoritos ---------------- */
  function getFavs() { try { return JSON.parse(localStorage.getItem(FAV_KEY)) || []; } catch (e) { return []; } }
  function setFavs(a) { try { localStorage.setItem(FAV_KEY, JSON.stringify(a)); } catch (e) {} }
  function isFav(id) { return getFavs().indexOf(id) >= 0; }
  function toggleFav(id) { var f = getFavs(), i = f.indexOf(id); if (i >= 0) f.splice(i, 1); else f.push(id); setFavs(f); renderSidebarFavs(); renderCards(); }

  /* ---------------- estado de filtro ---------------- */
  var estado = { termo: "", categoria: "todas" };
  function corresponde(it) {
    var t = semAcento(estado.termo);
    if (estado.categoria !== "todas" && it.id !== estado.categoria) return false;
    if (!t) return true;
    var alvo = semAcento(it.nome + " " + it.descricao + " " + (it.keywords || []).join(" ") + " " + (it.paineis || []).map(function (p) { return p.nome; }).join(" ") + " " + (it.tags || []).join(" "));
    return alvo.indexOf(t) >= 0;
  }

  var SVG_SETA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  var SVG_STAR = '<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>';
  var SVG_STAR_O = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>';

  /* ---------------- Visão Geral: cards ---------------- */
  function cardHTML(it, idx) {
    var fav = isFav(it.id);
    var subs = (it._subs || []).map(function (s) { return '<span class="sub-tag">' + s + "</span>"; }).join("");
    return (
      '<article class="card" style="--accent:' + it.cor + ';animation-delay:' + (idx * 55) + 'ms" data-id="' + it.id + '">' +
        '<div class="card-top">' +
          '<div class="card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + it.icone + "</svg></div>" +
          '<button class="fav-btn' + (fav ? " is-fav" : "") + '" data-fav="' + it.id + '" aria-pressed="' + fav + '" aria-label="' + (fav ? "Remover dos favoritos" : "Adicionar aos favoritos") + '" title="Favoritar">' + (fav ? SVG_STAR : SVG_STAR_O) + "</button>" +
        "</div>" +
        "<h3>" + it.nome + "</h3>" +
        '<p class="card-desc">' + it.descricao + "</p>" +
        (subs ? '<div class="sub-tags">' + subs + "</div>" : "") +
        '<div class="card-meta">' +
          "<span>Atualização <b>" + fmtData(it.atualizacao) + "</b></span>" +
          "<span>Registros <b>" + (it._temValor ? nf(it._registros) : "—") + "</b></span>" +
        "</div>" +
        badge(it._status) +
        '<a class="card-cta" href="' + it.href + '" aria-label="Acessar ' + it.nome + '">Acessar dashboard ' + SVG_SETA + "</a>" +
      "</article>"
    );
  }
  function renderCards() {
    var grid = el("cards"); if (!grid) return;
    var vis = ITENS.filter(corresponde);
    if (!vis.length) {
      grid.innerHTML = '<div class="empty-state" role="status"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg><p>Nenhum dashboard encontrado para o filtro atual.</p></div>';
      setText("results-info", "0 dashboards"); return;
    }
    grid.innerHTML = vis.map(cardHTML).join("");
    setText("results-info", vis.length + (vis.length === 1 ? " categoria" : " categorias") + (estado.termo ? ' para "' + estado.termo + '"' : "") + (estado.categoria !== "todas" ? " · filtro ativo" : ""));
  }

  /* ---------------- Operações: saúde ---------------- */
  function renderHealth() {
    var box = el("health-grid"); if (!box) return;
    var m = metrics();
    var itens = [
      ["online", "Portal BI", "Online"],
      ["online", "GitHub Pages", "Publicado"],
      ["online", "Framework", "Operacional"],
      ["online", "Design System", "Carregado"],
      ["online", "Auditoria", META.auditoria || "—"],
      ["online", "Dashboards", m.ativos + " ativos"],
      ["online", "Bases monitoradas", String(m.bases)],
      ["online", "Registros processados", nf(m.registros)],
      ["online", "Última atualização", fmtDataHora(META.ultimaAtualizacao)]
    ];
    box.innerHTML = itens.map(function (i) {
      return '<div class="health-item"><span class="st ' + i[0] + '"></span><div class="txt"><div class="k">' + i[1] + '</div><div class="v">' + i[2] + "</div></div></div>";
    }).join("");

    // Atenção: pendências reais (painéis fora de "online")
    var pend = [];
    todosPaineis().forEach(function (x) {
      var s = statusPainel(x.p);
      if (s !== "online") pend.push({ nome: x.p.nome, msg: x.p.pendencia || (s === "updating" ? "Dados parciais." : "Aguardando dados.") });
    });
    var att = el("attention");
    if (pend.length) {
      att.style.display = "flex";
      att.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4M12 17h.01M10.3 3.9L1.8 18a2 2 0 001.7 3h17a2 2 0 001.7-3L14.7 3.9a2 2 0 00-3.4 0z"/></svg>' +
        "<div><b>Atenção — " + pend.length + (pend.length === 1 ? " módulo" : " módulos") + " com pendência</b><ul>" +
        pend.map(function (p) { return "<li><b>" + p.nome + "</b> — " + p.msg + "</li>"; }).join("") + "</ul></div>";
    } else { att.style.display = "none"; }
  }

  /* ---------------- Operações: métricas ---------------- */
  function renderMetrics() {
    var box = el("metrics"); if (!box) return;
    var m = metrics();
    var cards = [
      [m.ativos, "Dashboards"], [m.categorias, "Categorias"], [m.bases, "Bases monitoradas"],
      [nf(m.registros), "Registros"], [META.framework || 1, "Framework"], [META.designSystem || 1, "Design System"],
      [fmtDataHora(META.ultimaAtualizacao), "Última sincronização"]
    ];
    box.innerHTML = cards.map(function (c) { return '<div class="metric"><div class="v">' + c[0] + '</div><div class="l">' + c[1] + "</div></div>"; }).join("");
  }

  /* ---------------- Operações: tabela de monitoramento ---------------- */
  function renderMonitor() {
    var tb = el("monitor-body"); if (!tb) return;
    var rows = [];
    todosPaineis().forEach(function (x) {
      var p = x.p, c = x.c, s = statusPainel(p);
      rows.push(
        "<tr>" +
          '<td><span class="name"><span class="dot-cat" style="background:' + c.cor + '"></span>' + p.nome + "</span></td>" +
          "<td>" + badge(s) + "</td>" +
          "<td>" + fmtData(p.atualizacao || c.atualizacao) + "</td>" +
          '<td class="num">' + (p.registrosLabel || nf(p.registros)) + "</td>" +
          '<td><span class="grp">' + c.grupo + "</span></td>" +
          '<td class="ver">' + c.versao + "</td>" +
        "</tr>"
      );
    });
    tb.innerHTML = rows.join("");
  }

  /* ---------------- Sobre + Histórico ---------------- */
  function li(arr) { return "<ul>" + arr.map(function (x) { return "<li>" + x + "</li>"; }).join("") + "</ul>"; }
  function renderSobre() {
    var s = META.sobre || {}; var box = el("about"); if (!box) return;
    var ico = function (d) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + d + "</svg>"; };
    box.innerHTML =
      '<div class="about-block about-full"><h4>' + ico('<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>') + "Objetivo do Portal</h4><p>" + (s.objetivo || "") + "</p></div>" +
      '<div class="about-block"><h4>' + ico('<path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-3"/>') + "Secretarias participantes</h4>" + li(s.secretarias || []) + "</div>" +
      '<div class="about-block"><h4>' + ico('<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0018 0V5"/>') + "Origem dos dados</h4>" + li(s.origemDados || []) + "</div>" +
      '<div class="about-block"><h4>' + ico('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>') + "Periodicidade de atualização</h4><p>" + (s.periodicidade || "") + "</p></div>" +
      '<div class="about-block"><h4>' + ico('<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>') + "Arquitetura</h4><p>" + (s.arquitetura || "") + "</p></div>" +
      '<div class="about-block"><h4>' + ico('<path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/>') + "Framework</h4><p>" + (s.framework || "") + "</p></div>" +
      '<div class="about-block"><h4>' + ico('<circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>') + "Design System</h4><p>" + (s.designSystem || "") + "</p></div>" +
      '<div class="about-block"><h4>' + ico('<path d="M12 2l2.4 7.4H22l-6 4.5 2.3 7.1L12 16.5 5.7 21l2.3-7.1-6-4.5h7.6z"/>') + "Tecnologias utilizadas</h4>" + li(s.tecnologias || []) + "</div>" +
      '<div class="about-block about-full"><h4>' + ico('<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>') + "Equipe responsável e contato técnico</h4>" +
        '<div class="kv"><div><div class="k">Equipe</div><div class="v">' + (s.equipe || "") + '</div></div>' +
        '<div><div class="k">Contato técnico</div><div class="v">' + (s.contato || "") + '</div></div>' +
        '<div><div class="k">Versão atual</div><div class="v">v' + (META.versao || "") + '</div></div>' +
        '<div><div class="k">Publicação</div><div class="v">' + (META.publicacao || "") + "</div></div></div></div>";
  }
  function renderChangelog() {
    var box = el("changelog"); if (!box) return;
    box.innerHTML = (META.changelog || []).map(function (v) {
      return '<div class="cl-item' + (v.atual ? " atual" : "") + '"><div class="cl-head"><span class="cl-ver">v' + v.versao + '</span><span class="cl-date">' + fmtData(v.data) + "</span>" +
        (v.atual ? '<span class="cl-tag">Atual</span>' : "") + "</div>" + li(v.itens) + "</div>";
    }).join("");
  }

  /* ---------------- rodapé ---------------- */
  function renderFooter() {
    var box = el("foot-grid"); if (!box) return;
    box.innerHTML =
      '<div class="foot-col"><div class="k">Portal</div><div class="v">Portal BI · Prefeitura de Joinville</div></div>' +
      '<div class="foot-col"><div class="k">Versão</div><div class="v">v' + (META.versao || "") + '</div></div>' +
      '<div class="foot-col"><div class="k">Última publicação</div><div class="v">' + (META.publicacao || "") + '</div></div>' +
      '<div class="foot-col"><div class="k">Secretaria responsável</div><div class="v">SEPUR · Unidade de Mobilidade</div></div>';
    setText("foot-year", new Date().getFullYear());
  }

  /* ---------------- sidebar ---------------- */
  function renderSidebarNav() {
    var nav = el("side-cats"); if (!nav) return;
    var html = '<li><button class="' + (estado.categoria === "todas" ? "is-active" : "") + '" data-cat="todas"><span class="dot-cat" style="background:var(--brand-400)"></span>Todas as categorias<span class="count">' + ITENS.length + "</span></button></li>";
    html += ITENS.map(function (it) {
      return '<li><button class="' + (estado.categoria === it.id ? "is-active" : "") + '" data-cat="' + it.id + '"><span class="dot-cat" style="background:' + it.cor + '"></span>' + it.nome + "</button></li>";
    }).join("");
    nav.innerHTML = html;
  }
  function renderSidebarFavs() {
    var box = el("side-favs"); if (!box) return;
    var favs = getFavs().map(function (id) { return ITENS.filter(function (i) { return i.id === id; })[0]; }).filter(Boolean);
    box.innerHTML = favs.length
      ? favs.map(function (it) { return '<li><a href="' + it.href + '"><span class="dot-cat" style="background:' + it.cor + '"></span>' + it.nome + '<span class="star" aria-hidden="true">★</span></a></li>'; }).join("")
      : '<li class="side-fav-empty">Nenhum favorito ainda. Toque na ⭐ de um card.</li>';
  }
  function renderChips() {
    var wrap = el("chips"); if (!wrap) return;
    wrap.innerHTML = '<button class="chip is-active" data-cat="todas">Todas</button>' +
      ITENS.map(function (it) { return '<button class="chip" data-cat="' + it.id + '"><span class="dot-cat" style="background:' + it.cor + '"></span>' + it.nome.replace(" UMO", "").replace(" SEPUR", "") + "</button>"; }).join("");
  }

  /* ---------------- hero stats ---------------- */
  function renderHeroStats() {
    var m = metrics();
    setText("stat-dashboards", m.ativos);
    setText("stat-bases", m.bases);
    setText("stat-registros", nf(m.registros));
    setText("stat-atualizacao", fmtData(CAT.atualizacao));
  }

  /* ---------------- views ---------------- */
  function setView(name) {
    var valid = ["geral", "operacoes", "sobre"];
    if (valid.indexOf(name) < 0) name = "geral";
    document.querySelectorAll(".view").forEach(function (v) { v.classList.toggle("is-active", v.getAttribute("data-view") === name); });
    document.querySelectorAll("[data-view]").forEach(function (b) { if (b.tagName === "BUTTON" || b.classList.contains("side-view")) b.classList.toggle("is-active", b.getAttribute("data-view") === name); });
    try { history.replaceState(null, "", "#" + name); } catch (e) {}
    document.querySelector(".content").scrollIntoView({ block: "start" });
    closeNav();
  }

  /* ---------------- tema ---------------- */
  function aplicarTema(t) {
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem(THEME_KEY, t); } catch (e) {}
    var btn = el("theme-toggle");
    if (btn) {
      var dark = t === "dark";
      btn.setAttribute("aria-pressed", dark);
      btn.setAttribute("aria-label", dark ? "Ativar tema claro" : "Ativar tema escuro");
      btn.innerHTML = dark
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1111.2 3 7 7 0 0021 12.8z"/></svg>';
    }
  }
  function temaInicial() { try { var s = localStorage.getItem(THEME_KEY); if (s) return s; } catch (e) {} return (window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches) ? "dark" : "light"; }

  /* ---------------- relógio ---------------- */
  function tickClock() {
    var now = new Date();
    setText("clock-t", pad(now.getHours()) + ":" + pad(now.getMinutes()) + ":" + pad(now.getSeconds()));
    setText("clock-d", WD[now.getDay()] + ", " + now.getDate() + " de " + MO[now.getMonth()] + " de " + now.getFullYear());
  }

  /* ---------------- eventos ---------------- */
  function closeNav() { var a = document.querySelector(".app"); if (a) a.classList.remove("nav-open"); }
  function bind() {
    var inputs = [el("search-main"), el("search-side")].filter(Boolean);
    inputs.forEach(function (inp) {
      inp.addEventListener("input", function () {
        estado.termo = inp.value.trim();
        inputs.forEach(function (o) { if (o !== inp) o.value = inp.value; });
        var sm = document.querySelector(".search-main"); if (sm) sm.classList.toggle("has-value", !!estado.termo);
        if (estado.termo) setView("geral");
        renderCards();
      });
    });
    var clear = el("search-clear");
    if (clear) clear.addEventListener("click", function () { estado.termo = ""; inputs.forEach(function (o) { o.value = ""; }); document.querySelector(".search-main").classList.remove("has-value"); renderCards(); inputs[0].focus(); });

    document.addEventListener("click", function (e) {
      var v = e.target.closest("[data-view]");
      if (v) { e.preventDefault(); setView(v.getAttribute("data-view")); return; }
      var catBtn = e.target.closest("[data-cat]");
      if (catBtn) {
        estado.categoria = catBtn.getAttribute("data-cat");
        document.querySelectorAll(".chip[data-cat]").forEach(function (c) { c.classList.toggle("is-active", c.getAttribute("data-cat") === estado.categoria); });
        renderSidebarNav(); setView("geral"); renderCards(); return;
      }
      var favBtn = e.target.closest("[data-fav]");
      if (favBtn) { e.preventDefault(); toggleFav(favBtn.getAttribute("data-fav")); }
    });

    var tt = el("theme-toggle");
    if (tt) tt.addEventListener("click", function () { aplicarTema(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark"); });
    var mt = el("menu-toggle");
    if (mt) mt.addEventListener("click", function () { document.querySelector(".app").classList.toggle("nav-open"); });
    var bd = el("backdrop");
    if (bd) bd.addEventListener("click", closeNav);

    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement.tagName !== "INPUT") { e.preventDefault(); inputs[0].focus(); }
      if (e.key === "Escape") closeNav();
    });
  }

  /* ---------------- init ---------------- */
  document.addEventListener("DOMContentLoaded", function () {
    enriquecer();
    aplicarTema(temaInicial());
    renderHeroStats();
    renderSidebarNav(); renderSidebarFavs(); renderChips(); renderCards();
    renderHealth(); renderMetrics(); renderMonitor();
    renderSobre(); renderChangelog(); renderFooter();
    tickClock(); setInterval(tickClock, 1000);
    bind();
    setView((location.hash || "").replace("#", "") || "geral");
  });
})();
