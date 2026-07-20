"""
comum.py — Utilitários compartilhados da automação do Portal BI.

Tudo aqui usa APENAS caminhos relativos, descobertos a partir da localização
deste arquivo. O projeto pode ser copiado para qualquer computador sem ajustes.

Estrutura esperada (raiz do projeto = pasta que contém as duas abaixo):

    <RAIZ>/
      Dashboards HTML/      (planilhas + geradores oficiais)
      portal-bi/            (site publicado + framework + automação)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------- CAMINHOS
AUTOMACAO = Path(__file__).resolve().parent          # <RAIZ>/portal-bi/automacao
PORTAL = AUTOMACAO.parent                            # <RAIZ>/portal-bi
RAIZ = PORTAL.parent                                 # <RAIZ>
DADOS = RAIZ / "Dashboards HTML"                     # planilhas + geradores
FRAMEWORK = PORTAL / "framework-dashboards"
RESKIN = FRAMEWORK / "reskin"
LOGS = RAIZ / "logs"

URL_BASE = "https://pmj-sepud.github.io/portal-bi/"


# ------------------------------------------------------------------- ERROS
class FalhaAutomacao(Exception):
    """Erro de automação com mensagem clara para o usuário final."""


# -------------------------------------------------------------------- LOG
class Log:
    def __init__(self, dashboard_id: str):
        LOGS.mkdir(exist_ok=True)
        carimbo = datetime.now().strftime("%Y-%m-%d_%H%M")
        self.caminho = LOGS / f"{dashboard_id}_{carimbo}.log"
        self._linhas: list[str] = []
        self.inicio = time.time()

    def __call__(self, msg: str = "") -> None:
        print(msg)
        self._linhas.append(msg)

    def titulo(self, msg: str) -> None:
        self("")
        self("=" * 68)
        self(f"  {msg}")
        self("=" * 68)

    def salvar(self) -> Path:
        self("")
        self(f"Tempo total: {time.time() - self.inicio:.1f}s")
        self.caminho.write_text("\n".join(self._linhas), encoding="utf-8")
        return self.caminho


# ------------------------------------------------------------- PRÉ-REQUISITOS
def checar_prerequisitos(log: Log) -> None:
    """Verifica Python e Git antes de qualquer coisa."""
    log(f"Python  : {sys.version.split()[0]}  ({sys.executable})")
    if shutil.which("git") is None:
        raise FalhaAutomacao(
            "GIT NAO ENCONTRADO.\n"
            "  Instale o Git em https://git-scm.com/downloads e reabra o terminal.\n"
            "  Sem o Git nao e possivel publicar no GitHub Pages."
        )
    ver = _run(["git", "--version"], cwd=PORTAL).stdout.strip()
    log(f"Git     : {ver}")
    if not (PORTAL / ".git").exists():
        raise FalhaAutomacao(
            f"REPOSITORIO GIT NAO ENCONTRADO em {PORTAL}.\n"
            "  A pasta 'portal-bi' precisa conter o repositorio (.git) do Portal."
        )


def _run(cmd, cwd=None, entrada=None, timeout=900) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, input=entrada, timeout=timeout,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


# ---------------------------------------------------------------- PLANILHA
def localizar_planilha(pasta: Path, arquivo: str | None, log: Log) -> Path:
    """Localiza a planilha da PRÓPRIA pasta (nunca caminho absoluto fixo)."""
    if not pasta.exists():
        raise FalhaAutomacao(f"PASTA DA FONTE NAO ENCONTRADA:\n  {pasta}")
    if arquivo:
        p = pasta / arquivo
        if not p.exists():
            raise FalhaAutomacao(
                f"PLANILHA INEXISTENTE:\n  {p}\n"
                "  Coloque a planilha atualizada nesta pasta, com o mesmo nome."
            )
        return p
    candidatos = [f for f in pasta.glob("*.xlsx") if not f.name.startswith("~")]
    if not candidatos:
        raise FalhaAutomacao(f"NENHUMA PLANILHA .xlsx ENCONTRADA EM:\n  {pasta}")
    return sorted(candidatos)[0]


# ---------------------------------------------------------------- GERADOR
# Aceita "4090 registros processados", "Registros: 218,454" e "Total de registros: 77".
# Exige DIGITO inicial para nao confundir reticencias ("aguarde...") com numero.
_RE_CONTAGEM = re.compile(
    r"(\d[\d.,]{0,14})\s+registros|registros\s*:\s*(\d[\d.,]{0,14})", re.IGNORECASE
)


def rodar_gerador(pasta: Path, script: str, log: Log) -> tuple[str, int | None]:
    """Executa o gerador OFICIAL da pasta (nunca edita HTML manualmente)."""
    alvo = pasta / script
    if not alvo.exists():
        raise FalhaAutomacao(f"GERADOR OFICIAL NAO ENCONTRADO:\n  {alvo}")
    log(f"Executando gerador oficial: {script}")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run(
        [sys.executable, script], cwd=str(pasta), input="\n\n",
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=1800, env=env,
    )
    saida = (proc.stdout or "") + (proc.stderr or "")
    for linha in saida.splitlines():
        if linha.strip():
            log(f"  | {linha.strip()}")
    if proc.returncode != 0 and "Traceback" in saida:
        raise FalhaAutomacao(f"ERRO AO EXECUTAR O GERADOR '{script}':\n{saida[-1500:]}")

    contagem = None
    for antes, depois in _RE_CONTAGEM.findall(saida):
        bruto = antes or depois
        try:
            contagem = int(bruto.replace(".", "").replace(",", ""))
        except ValueError:
            continue
    return saida, contagem


# ---------------------------------------------------------------- AUDITORIA
def contar_registros_html(html: str) -> int | None:
    """Conta registros embutidos no HTML (tenta os formatos conhecidos)."""
    for marcador in ("const RAW_DATA = ", "const DADOS = ", "const RAW = ", "const P = ", "const D = "):
        i = html.find(marcador)
        if i < 0:
            continue
        j = html.find("[", i)
        k = html.find("{", i)
        try:
            dec = json.JSONDecoder()
            if 0 <= j < (k if k >= 0 else 10**9):
                dados, _ = dec.raw_decode(html, j)
                if isinstance(dados, list):
                    return len(dados)
            elif k >= 0:
                dados, _ = dec.raw_decode(html, k)
                if isinstance(dados, dict):
                    # dashboards agregados guardam as linhas em 'registros'/'rows'/'dados'
                    for chave in ("registros", "rows", "dados"):
                        if isinstance(dados.get(chave), list):
                            return len(dados[chave])
                    # senao, os registros vivem em arrays paralelos: o maior deles é o total
                    tamanhos = [len(v) for v in dados.values() if isinstance(v, list)]
                    if tamanhos:
                        return max(tamanhos)
        except Exception:
            continue

    # Dashboards do tipo "portal" guardam os dados em <script id="data-payload">
    # como JSON, com os registros num campo-texto "data" separado por '|'.
    m = re.search(r'id="data-payload"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            dados = json.loads(m.group(1))
            serie = dados.get("data")
            if isinstance(serie, str):
                return serie.count("|") + 1 if serie else 0
        except Exception:
            pass
    return None


def auditar_bespoke(html_path: Path, contagem_gerador: int | None, log: Log) -> int | None:
    """
    Auditoria Planilha -> Gerador -> Dashboard para geradores próprios.
    O gerador lê a planilha e informa quantos registros processou; conferimos
    que exatamente esse total chegou ao HTML. Divergência => PARA.
    """
    if not html_path.exists():
        raise FalhaAutomacao(f"O GERADOR NAO PRODUZIU O HTML ESPERADO:\n  {html_path}")
    html = html_path.read_text(encoding="utf-8", errors="replace")
    embutidos = contar_registros_html(html)

    log("")
    log("--- Auditoria (Planilha -> Gerador -> Dashboard) ---")
    log(f"  Registros informados pelo gerador : {contagem_gerador if contagem_gerador is not None else '—'}")
    log(f"  Registros embutidos no dashboard  : {embutidos if embutidos is not None else '—'}")

    if contagem_gerador is not None and embutidos is not None:
        if contagem_gerador != embutidos:
            raise FalhaAutomacao(
                "DIVERGENCIA NA AUDITORIA — PUBLICACAO ABORTADA.\n"
                f"  Gerador processou {contagem_gerador} registros, "
                f"mas o dashboard embutiu {embutidos}.\n"
                "  Nada foi publicado. Verifique a planilha e o gerador."
            )
        log("  [OK] Correspondencia 100% (gerador == dashboard)")
        return embutidos

    if embutidos is not None:
        log("  [OK] Dashboard regenerado (contagem do gerador nao informada)")
        return embutidos
    if contagem_gerador is not None:
        # Dashboard com dados agregados (sem array linha-a-linha): confere pelo total exibido.
        alvo = f"{contagem_gerador:,}".replace(",", ".")
        if alvo in html or str(contagem_gerador) in html:
            log(f"  [OK] Total {alvo} presente no dashboard")
            return contagem_gerador
        raise FalhaAutomacao(
            "DIVERGENCIA NA AUDITORIA — PUBLICACAO ABORTADA.\n"
            f"  O total de {contagem_gerador} registros nao foi localizado no dashboard gerado."
        )
    raise FalhaAutomacao("AUDITORIA IMPOSSIVEL: nao foi possivel contar registros.")


# --------------------------------------------------------------- INTEGRAÇÃO
def integrar_no_portal(html_origem: Path, destino_rel: str, profundidade: str, log: Log) -> None:
    """Embute o HTML gerado na página do Portal, preservando chrome e reskin."""
    destino = PORTAL / destino_rel
    if not destino.exists():
        raise FalhaAutomacao(f"PAGINA DO PORTAL NAO ENCONTRADA:\n  {destino}")
    html = html_origem.read_text(encoding="utf-8", errors="replace")
    m_head = re.search(r"<head[^>]*>(.*)</head>", html, re.DOTALL | re.IGNORECASE)
    m_body = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
    if not (m_head and m_body):
        raise FalhaAutomacao(f"HTML GERADO INVALIDO (sem <head>/<body>):\n  {html_origem}")

    head = "\n".join("  " + l if l.strip() else l for l in m_head.group(1).strip().splitlines())
    body = m_body.group(1).strip()
    antigo = destino.read_text(encoding="utf-8")

    novo, n_head = re.subn(
        r"(<head>\n)(.*?)(\n  <link rel=\"stylesheet\" href=\"" + re.escape(profundidade) + r"assets/css/dashboard\.css\")",
        lambda m: m.group(1) + head + m.group(3), antigo, flags=re.DOTALL,
    )
    novo, n_body = re.subn(
        r"(<div class=\"pbi-embedded-dashboard\">\n)(.*?)(\n  </div>\n\n  <!-- ={5,}\n       RODAP)",
        lambda m: m.group(1) + body + m.group(3), novo, flags=re.DOTALL,
    )
    if n_head != 1 or n_body != 1:
        raise FalhaAutomacao(
            "FALHA AO EMBUTIR NO PORTAL (marcadores do wrapper nao encontrados):\n"
            f"  {destino}\n  head={n_head} body={n_body}"
        )
    destino.write_text(novo, encoding="utf-8")
    inalterado = " (conteudo identico ao publicado)" if novo == antigo else ""
    log(f"Integrado no Portal: {destino_rel}{inalterado}")


def aplicar_reskin(destino_rel: str, arquivo_css: str, log: Log) -> None:
    """Reaplica o override visual (identidade azul) do dashboard bespoke."""
    css_path = RESKIN / arquivo_css
    if not css_path.exists():
        log(f"AVISO: reskin '{arquivo_css}' nao encontrado; seguindo sem reaplicar.")
        return
    destino = PORTAL / destino_rel
    html = destino.read_text(encoding="utf-8")
    bloco = f'<style id="bi-reskin">\n{css_path.read_text(encoding="utf-8")}\n</style>'
    if 'id="bi-reskin"' in html:
        html = re.sub(r'<style id="bi-reskin">.*?</style>', lambda _: bloco, html, flags=re.DOTALL)
    else:
        html = html.replace("</head>", bloco + "\n</head>", 1)
    destino.write_text(html, encoding="utf-8")
    log(f"Identidade visual reaplicada: reskin/{arquivo_css}")


# ------------------------------------------------------------- CATALOG.JS
CATALOG = PORTAL / "assets" / "js" / "catalog.js"


def atualizar_catalog(paineis: dict[str, int], categoria_id: str | None, log: Log) -> None:
    """
    Atualiza os DADOS do Centro de Operações (contagem, data, sincronização).
    Não altera estrutura, layout nem componentes.
    """
    if not CATALOG.exists():
        raise FalhaAutomacao(f"catalog.js NAO ENCONTRADO:\n  {CATALOG}")
    hoje = datetime.now().strftime("%Y-%m-%d")
    agora = datetime.now().strftime("%Y-%m-%dT%H:%M")
    texto = CATALOG.read_text(encoding="utf-8")
    linhas = texto.splitlines()

    for nome, total in paineis.items():
        alvo = f'nome: "{nome}"'
        for i, linha in enumerate(linhas):
            if alvo in linha:
                nova = re.sub(r"registros: \d+", f"registros: {total}", linha)
                nova = re.sub(r'atualizacao: "[^"]*"', f'atualizacao: "{hoje}"', nova)
                linhas[i] = nova
                log(f"  catalog.js: {nome} -> {total:,} registros ({hoje})".replace(",", "."))
                break
        else:
            log(f"  AVISO: painel '{nome}' nao encontrado no catalog.js")

    texto = "\n".join(linhas)
    if categoria_id:
        texto = re.sub(
            r'(href: "dashboards/' + re.escape(categoria_id) + r'/", bases: \d+, atualizacao: )"[^"]*"',
            lambda m: m.group(1) + f'"{hoje}"', texto,
        )
    texto = re.sub(r'atualizacao: "\d{4}-\d{2}-\d{2}",\n  categorias:',
                   f'atualizacao: "{hoje}",\n  categorias:', texto)
    texto = re.sub(r'ultimaAtualizacao: "[^"]*"', f'ultimaAtualizacao: "{agora}"', texto)
    CATALOG.write_text(texto, encoding="utf-8")
    log(f"  catalog.js: ultima sincronizacao -> {agora}")


# ------------------------------------------------------------------- GIT
def git_publicar(mensagem: str, log: Log) -> bool:
    """git add + commit + push. Retorna False se nao havia nada a publicar."""
    log("")
    log("--- Publicacao (Git) ---")
    _run(["git", "add", "-A"], cwd=PORTAL)
    status = _run(["git", "status", "--porcelain"], cwd=PORTAL).stdout.strip()
    if not status:
        log("  Nada a publicar (nenhuma alteracao).")
        return False

    c = _run(["git", "commit", "-m", mensagem], cwd=PORTAL)
    if c.returncode != 0:
        raise FalhaAutomacao(f"ERRO NO COMMIT:\n{c.stdout}\n{c.stderr}")
    log(f"  Commit: {mensagem}")

    p = _run(["git", "push", "origin", "HEAD"], cwd=PORTAL, timeout=600)
    if p.returncode != 0:
        raise FalhaAutomacao(
            "ERRO NO PUSH PARA O GITHUB.\n"
            "  Verifique sua conexao e se voce tem permissao de escrita no repositorio.\n"
            f"  Detalhe: {(p.stderr or p.stdout).strip()[:400]}"
        )
    log("  Push enviado para o GitHub.")
    return True


# -------------------------------------------------------- GITHUB PAGES
def aguardar_publicacao(url: str, log: Log, tentativas: int = 30, espera: int = 8) -> bool:
    """Aguarda o GitHub Pages publicar e confirma HTTP 200."""
    log("")
    log("--- GitHub Pages ---")
    log(f"  Aguardando publicacao de: {url}")
    for i in range(1, tentativas + 1):
        try:
            req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status == 200:
                    log(f"  [OK] HTTP 200 confirmado (tentativa {i}).")
                    return True
        except Exception:
            pass
        time.sleep(espera)
    log("  AVISO: nao foi possivel confirmar HTTP 200 no tempo esperado.")
    log("  A publicacao pode levar mais alguns minutos. Verifique manualmente.")
    return False


def abrir_navegador(url: str, log: Log) -> None:
    try:
        webbrowser.open(url)
        log(f"  Abrindo no navegador: {url}")
    except Exception as e:
        log(f"  AVISO: nao foi possivel abrir o navegador ({e}).")
