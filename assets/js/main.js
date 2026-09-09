/**
 * main.js — Módulo compartilhado do Portal de Business Intelligence
 * Responsável por: relógio em tempo real e animação de entrada dos cards.
 * Reutilizado tanto na página inicial quanto no chrome de cada dashboard.
 */

(function () {
  'use strict';

  const WEEKDAYS = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado'];
  const MONTHS = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

  function pad(n) {
    return String(n).padStart(2, '0');
  }

  function formatDate(date) {
    return `${WEEKDAYS[date.getDay()]}, ${date.getDate()} de ${MONTHS[date.getMonth()]} de ${date.getFullYear()}`;
  }

  function formatTime(date) {
    return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  }

  /** Atualiza todos os elementos de relógio presentes na página (navbar principal e chrome dos dashboards). */
  function tickClock() {
    const now = new Date();
    const timeEls = document.querySelectorAll('[data-clock-time]');
    const dateEls = document.querySelectorAll('[data-clock-date]');
    timeEls.forEach((el) => { el.textContent = formatTime(now); });
    dateEls.forEach((el) => { el.textContent = formatDate(now); });
  }

  function initClock() {
    if (!document.querySelector('[data-clock-time]')) return;
    tickClock();
    setInterval(tickClock, 1000);
  }

  /** Aplica um pequeno atraso escalonado (stagger) na animação de entrada dos cards do portal. */
  function initCardStagger() {
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach((card, index) => {
      card.style.animationDelay = `${index * 70}ms`;
    });
  }

  /**
   * Agrupa o conteúdo do breadcrumb (trilha + título) num contêiner de bloco,
   * necessário porque .pbi-breadcrumb é flex-row: sem esse agrupamento, a
   * trilha e o <h1> ficam lado a lado em vez de empilhados. Idempotente.
   */
  function initBreadcrumbLayout() {
    const bc = document.querySelector('.pbi-breadcrumb');
    if (!bc || bc.querySelector('.pbi-breadcrumb-text')) return;
    const text = document.createElement('div');
    text.className = 'pbi-breadcrumb-text';
    while (bc.firstChild) text.appendChild(bc.firstChild);
    bc.appendChild(text);
  }

  document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initCardStagger();
    initBreadcrumbLayout();
  });
})();
