/**
 * portal.js — Motor da home do Portal BI.
 * Renderiza os cards a partir do catálogo (catalog.js), com busca em tempo real,
 * favoritos, filtro por categoria, badges de status automáticos, tema claro/escuro,
 * contadores institucionais e relógio. Sem dependências externas.
 */
(function () {
  "use strict";

  var CAT = (window.PORTAL_CATALOG || { categorias: [] });
  var ITENS = CAT.categorias;
  var FAV_KEY = "portalbi:favoritos";
  var THEME_KEY = "portalbi:tema";

  /* ---------- utilidades ---------- */
  var WD = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"];
  var MO = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  function pad(n) { return String(n).padStart(2, "0"); }
  function nf(n) { return (n == null) ? "—" : n.toLocaleString("pt-BR"); }
  function fmtData(iso) {
    if (!iso) return "—";
    var d = new Date(iso + "T00:00:00");
    return pad(d.getDate()) + "/" + pad(d.getMonth() + 1) + "/" + d.getFullYear();
  }
  function semAcento(s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }

  /* ---------- status automático ---------- */
  function statusDe(it) {
    if (it.registros == null) return { cls: "pending", txt: "Dados pendentes" };
    if (it.updating) return { cls: "updating", txt: "Atualizando" };
    return { cls: "ok", txt: "Atualizado" };
  }

  /* ---------- favoritos ---------- */
  function getFavs() { try { return JSON.parse(localStorage.getItem(FAV_KEY)) || []; } catch (e) { return []; } }
  function setFavs(a) { try { localStorage.setItem(FAV_KEY, JSON.stringify(a)); } catch (e) {} }
  function isFav(id) { return getFavs().indexOf(id) >= 0; }
  function toggleFav(id) {
    var f = getFavs(); var i = f.indexOf(id);
    if (i >= 0) f.splice(i, 1); else f.push(id);
    setFavs(f); renderSidebarFavs(); renderCards();
  }

  /* ---------- estado de filtro ---------- */
  var estado = { termo: "", categoria: "todas" };

  function corresponde(it) {
    var t = semAcento(estado.termo);
    if (estado.categoria !== "todas" && it.id !== estado.categoria) return false;
    if (!t) return true;
    var alvo = semAcento(it.nome + " " + it.descricao + " " + (it.keywords || []).join(" ") + " " + (it.subpaineis || []).join(" "));
    return alvo.indexOf(t) >= 0;
  }

  /* ---------- render cards ---------- */
  var SVG_SETA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  var SVG_STAR = '<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>';
  var SVG_STAR_O = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>';

  function cardHTML(it, idx) {
    var st = statusDe(it);
    var fav = isFav(it.id);
    var subs = (it.subpaineis || []).map(function (s) { return '<span class="sub-tag">' + s + "</span>"; }).join("");
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
          "<span>Última atualização <b>" + fmtData(it.atualizacao) + "</b></span>" +
          "<span>Registros <b>" + nf(it.registros) + "</b></span>" +
        "</div>" +
        '<span class="badge ' + st.cls + '">' + st.txt + "</span>" +
        '<a class="card-cta" href="' + it.href + '" aria-label="Acessar ' + it.nome + '">Acessar dashboard ' + SVG_SETA + "</a>" +
      "</article>"
    );
  }

  function renderCards() {
    var grid = document.getElementById("cards");
    var vis = ITENS.filter(corresponde);
    var info = document.getElementById("results-info");
    if (!vis.length) {
      grid.innerHTML = '<div class="empty-state" role="status"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg><p>Nenhum dashboard encontrado para o filtro atual.</p></div>';
      info.textContent = "0 dashboards";
      return;
    }
    grid.innerHTML = vis.map(cardHTML).join("");
    info.textContent = vis.length + (vis.length === 1 ? " dashboard" : " dashboards") +
      (estado.termo ? ' para "' + estado.termo + '"' : "") +
      (estado.categoria !== "todas" ? " · categoria filtrada" : "");
  }

  /* ---------- sidebar ---------- */
  function renderSidebarNav() {
    var nav = document.getElementById("side-cats");
    var html = '<li><button class="' + (estado.categoria === "todas" ? "is-active" : "") + '" data-cat="todas"><span class="dot-cat" style="background:var(--brand-400)"></span>Todas as categorias<span class="count">' + ITENS.length + "</span></button></li>";
    html += ITENS.map(function (it) {
      return '<li><button class="' + (estado.categoria === it.id ? "is-active" : "") + '" data-cat="' + it.id + '"><span class="dot-cat" style="background:' + it.cor + '"></span>' + it.nome + "</button></li>";
    }).join("");
    nav.innerHTML = html;
  }
  function renderSidebarFavs() {
    var box = document.getElementById("side-favs");
    var favs = getFavs().map(function (id) { return ITENS.filter(function (i) { return i.id === id; })[0]; }).filter(Boolean);
    if (!favs.length) { box.innerHTML = '<li class="side-fav-empty">Nenhum favorito ainda. Toque na ⭐ de um card.</li>'; return; }
    box.innerHTML = favs.map(function (it) {
      return '<li><a href="' + it.href + '"><span class="dot-cat" style="background:' + it.cor + '"></span>' + it.nome + '<span class="star" aria-hidden="true">★</span></a></li>';
    }).join("");
  }

  /* ---------- contadores institucionais ---------- */
  function renderContadores() {
    var totalReg = ITENS.reduce(function (s, i) { return s + (i.registros || 0); }, 0);
    var totalBases = ITENS.reduce(function (s, i) { return s + (i.bases || 0); }, 0);
    setText("stat-dashboards", ITENS.length);
    setText("stat-bases", totalBases);
    setText("stat-registros", nf(totalReg));
    setText("stat-atualizacao", fmtData(CAT.atualizacao));
  }
  function setText(id, v) { var e = document.getElementById(id); if (e) e.textContent = v; }

  /* ---------- tema ---------- */
  function aplicarTema(t) {
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem(THEME_KEY, t); } catch (e) {}
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      var dark = t === "dark";
      btn.setAttribute("aria-pressed", dark);
      btn.setAttribute("aria-label", dark ? "Ativar tema claro" : "Ativar tema escuro");
      btn.innerHTML = dark
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1111.2 3 7 7 0 0021 12.8z"/></svg>';
    }
  }
  function temaInicial() {
    try {
      var s = localStorage.getItem(THEME_KEY);
      if (s) return s;
    } catch (e) {}
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  /* ---------- relógio ---------- */
  function tickClock() {
    var now = new Date();
    setText("clock-t", pad(now.getHours()) + ":" + pad(now.getMinutes()) + ":" + pad(now.getSeconds()));
    setText("clock-d", WD[now.getDay()] + ", " + now.getDate() + " de " + MO[now.getMonth()] + " de " + now.getFullYear());
  }

  /* ---------- eventos ---------- */
  function bind() {
    // busca (principal + sidebar sincronizadas)
    var inputs = [document.getElementById("search-main"), document.getElementById("search-side")].filter(Boolean);
    inputs.forEach(function (inp) {
      inp.addEventListener("input", function () {
        estado.termo = inp.value.trim();
        inputs.forEach(function (o) { if (o !== inp) o.value = inp.value; });
        document.querySelector(".search-main").classList.toggle("has-value", !!estado.termo);
        renderCards();
      });
    });
    var clear = document.getElementById("search-clear");
    if (clear) clear.addEventListener("click", function () {
      estado.termo = ""; inputs.forEach(function (o) { o.value = ""; });
      document.querySelector(".search-main").classList.remove("has-value");
      renderCards(); inputs[0].focus();
    });

    // categorias (delegação: chips + sidebar)
    document.addEventListener("click", function (e) {
      var catBtn = e.target.closest("[data-cat]");
      if (catBtn) {
        estado.categoria = catBtn.getAttribute("data-cat");
        document.querySelectorAll(".chip[data-cat]").forEach(function (c) { c.classList.toggle("is-active", c.getAttribute("data-cat") === estado.categoria); });
        renderSidebarNav(); renderCards();
        closeNav();
        return;
      }
      var favBtn = e.target.closest("[data-fav]");
      if (favBtn) { e.preventDefault(); toggleFav(favBtn.getAttribute("data-fav")); }
    });

    // tema
    var tt = document.getElementById("theme-toggle");
    if (tt) tt.addEventListener("click", function () {
      var atual = document.documentElement.getAttribute("data-theme");
      aplicarTema(atual === "dark" ? "light" : "dark");
    });

    // menu mobile
    var mt = document.getElementById("menu-toggle");
    if (mt) mt.addEventListener("click", function () { document.querySelector(".app").classList.toggle("nav-open"); });
    var bd = document.getElementById("backdrop");
    if (bd) bd.addEventListener("click", closeNav);

    // atalho: "/" foca a busca
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement.tagName !== "INPUT") { e.preventDefault(); inputs[0].focus(); }
      if (e.key === "Escape") { closeNav(); }
    });
  }
  function closeNav() { document.querySelector(".app").classList.remove("nav-open"); }

  /* ---------- init ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    aplicarTema(temaInicial());
    renderContadores();
    renderSidebarNav();
    renderSidebarFavs();
    renderChips();
    renderCards();
    tickClock(); setInterval(tickClock, 1000);
    bind();
  });

  function renderChips() {
    var wrap = document.getElementById("chips");
    if (!wrap) return;
    var html = '<button class="chip is-active" data-cat="todas">Todas</button>';
    html += ITENS.map(function (it) {
      return '<button class="chip" data-cat="' + it.id + '"><span class="dot-cat" style="background:' + it.cor + '"></span>' + it.nome.replace(" UMO", "").replace(" SEPUR", "") + "</button>";
    }).join("");
    wrap.innerHTML = html;
  }
})();
