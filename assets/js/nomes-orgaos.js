/* Nomes completos dos orgaos da PMJ.
   Troca a sigla pelo nome completo so no texto exibido (dados, filtros e busca seguem com a sigla).
   Nao troca: codigos de unidade (ex.: SAMA.UAT), sigla ja entre parenteses apos o nome, nem o nome
   do programa "MVP SEPUR Programa de Intraempreendedorismo". Acompanha conteudo gerado depois (MutationObserver). */
(function () {
  var N = {
    GAP: "Gabinete do Prefeito",
    GVP: "Gabinete da Vice-Prefeita",
    PGM: "Procuradoria-Geral do Município",
    CGM: "Controladoria-Geral do Município",
    SEFAZ: "Secretaria da Fazenda",
    SES: "Secretaria da Saúde",
    SAP: "Secretaria de Administração e Planejamento",
    SAS: "Secretaria de Assistência Social",
    SECOM: "Secretaria de Comunicação",
    SECULT: "Secretaria de Cultura e Turismo",
    SDE: "Secretaria de Desenvolvimento Econômico e Inovação",
    SED: "Secretaria de Educação",
    SESPORTE: "Secretaria de Esportes",
    SGP: "Secretaria de Gestão de Pessoas",
    SEGOV: "Secretaria de Governo",
    SEHAB: "Secretaria de Habitação",
    SEINFRA: "Secretaria de Infraestrutura Urbana",
    SAMA: "Secretaria de Meio Ambiente",
    SEPUR: "Secretaria de Planejamento Urbano",
    SEPROT: "Secretaria de Proteção Civil e Segurança Pública",
    CAJ: "Companhia Águas de Joinville",
    DETRANS: "Departamento de Trânsito de Joinville",
    HMSJ: "Hospital Municipal São José",
    IPREVILLE: "Instituto de Previdência dos Servidores Públicos do Município de Joinville"
  };
  var L = "A-Za-z0-9_À-ÿ";
  var RE = new RegExp("(^|[^" + L + ".])(" + Object.keys(N).join("|") + ")(?![" + L + "]|\\.[A-Za-z])", "g");
  var PROGRAMA = /^\s*Programa de Intraempreendedorismo/;

  function troca(s) {
    return s.replace(RE, function (m, antes, sigla, pos, str) {
      if (antes === "(" && str.charAt(pos + m.length) === ")") return m;  // "Nome completo (SIGLA)"
      if (sigla === "SEPUR" && PROGRAMA.test(str.slice(pos + m.length)) &&
          /MVP\s*$/.test(str.slice(0, pos + antes.length))) return m;
      return antes + N[sigla];
    });
  }

  var PULA = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, CODE: 1, NOSCRIPT: 1, INPUT: 1 };
  var ATRIBUTOS = ["placeholder", "title", "aria-label"];

  function varre(no) {
    if (!no) return;
    if (no.nodeType === 3) {
      var t = troca(no.nodeValue);
      if (t !== no.nodeValue) no.nodeValue = t;
      return;
    }
    if (no.nodeType !== 1 || PULA[no.nodeName]) {
      if (no.nodeName === "INPUT") troca_atributos(no);
      return;
    }
    troca_atributos(no);
    for (var c = no.firstChild; c; c = c.nextSibling) varre(c);
  }

  function troca_atributos(el) {
    ATRIBUTOS.forEach(function (a) {
      var v = el.getAttribute(a);
      if (v) { var t = troca(v); if (t !== v) el.setAttribute(a, t); }
    });
  }

  function inicia() {
    varre(document.body);
    document.title = troca(document.title);
    new MutationObserver(function (ms) {
      ms.forEach(function (m) {
        if (m.type === "characterData") varre(m.target);
        else m.addedNodes.forEach(varre);
      });
    }).observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicia);
  else inicia();
})();
