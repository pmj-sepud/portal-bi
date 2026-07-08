"""
carregar_planilha.py — Camada de DADOS.

Responsabilidade única: ler as planilhas de origem e devolver os registros
brutos, sem qualquer transformação analítica. Não calcula KPIs nem agrega —
isso é responsabilidade do processador. Nunca escreve na planilha.

Suporta dois tipos de fonte declarados na configuração:

  • "eventos"        — uma planilha, uma aba, uma linha por ocorrência.
  • "ranking_mensal" — vários arquivos (um por mês), várias abas (uma por
                       período do dia), cada linha já é um ranking pronto.
"""

from pathlib import Path
import re
import unicodedata
import pandas as pd

MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _sem_acento(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def _mes_para_indice(nome_mes: str):
    alvo = _sem_acento(nome_mes)
    for i, m in enumerate(MESES_PT):
        if _sem_acento(m) == alvo:
            return i + 1  # 1..12
    return None


def carregar(config: dict, base_dir: Path) -> dict:
    """
    Roteia para o leitor adequado conforme config['fonte']['tipo'].

    Retorna um dicionário 'bruto' com:
      - tipo: "eventos" | "ranking_mensal"
      - para eventos:  {"registros": DataFrame com colunas normalizadas}
      - para ranking:  {"meses": [ {ano, mes, periodo, DataFrame}, ... ]}
    """
    fonte = config["fonte"]
    tipo = fonte["tipo"]
    if tipo == "eventos":
        return _carregar_eventos(fonte, base_dir)
    if tipo == "ranking_mensal":
        return _carregar_ranking_mensal(fonte, base_dir)
    raise ValueError(f"Tipo de fonte desconhecido: {tipo!r}")


# ---------------------------------------------------------------------------
# Fonte "eventos": 1 arquivo, 1 aba, 1 linha por ocorrência
# ---------------------------------------------------------------------------
def _carregar_eventos(fonte: dict, base_dir: Path) -> dict:
    caminho = base_dir / fonte["arquivo"]
    if not caminho.exists():
        raise FileNotFoundError(f"Planilha de origem não encontrada: {caminho}")

    aba = fonte.get("aba", 0)
    df = pd.read_excel(caminho, sheet_name=aba)

    cols = fonte["colunas"]  # mapeia papel -> nome da coluna na planilha
    saida = pd.DataFrame()

    # Data (obrigatória para dashboards temporais)
    saida["_data"] = pd.to_datetime(df[cols["data"]], errors="coerce", dayfirst=True)

    if "hora" in cols and cols["hora"] in df.columns:
        saida["_hora"] = df[cols["hora"]].apply(_extrair_hora)
    else:
        saida["_hora"] = -1  # sem informação de hora nesta fonte

    saida["_rua"] = (
        df[cols["rua"]].fillna("Desconhecida").astype(str).str.strip()
        if "rua" in cols else "Desconhecida"
    )
    saida["_lat"] = pd.to_numeric(df[cols["lat"]], errors="coerce") if "lat" in cols else None
    saida["_lng"] = pd.to_numeric(df[cols["lng"]], errors="coerce") if "lng" in cols else None

    total_planilha = len(df)
    # A única exclusão permitida é a de linhas sem data válida — sem data não há
    # como posicioná-las no eixo temporal. Elas são contabilizadas e reportadas.
    validas = saida["_data"].notna()
    descartadas = int((~validas).sum())
    saida = saida[validas].copy()

    return {
        "tipo": "eventos",
        "registros": saida,
        "diag": {
            "linhas_planilha": total_planilha,
            "linhas_sem_data": descartadas,
            "linhas_usadas": len(saida),
            "arquivo": str(caminho.name),
            "aba": aba,
        },
    }


def _extrair_hora(valor):
    """Extrai a hora (0..23) de um valor de célula que pode ser time/datetime/str."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return -1
    if hasattr(valor, "hour"):
        return int(valor.hour)
    m = re.match(r"\s*(\d{1,2})[:h]", str(valor))
    if m:
        h = int(m.group(1))
        return h if 0 <= h <= 23 else -1
    return -1


# ---------------------------------------------------------------------------
# Fonte "ranking_mensal": N arquivos (um por mês) x M abas (uma por período)
# ---------------------------------------------------------------------------
def _carregar_ranking_mensal(fonte: dict, base_dir: Path) -> dict:
    pasta = base_dir / fonte["pasta"]
    if not pasta.exists():
        raise FileNotFoundError(f"Pasta de rankings não encontrada: {pasta}")

    # Ex.: "Ranking Waze {mes} {ano}.xlsx"  ->  regex tolerante a acentos
    padrao = fonte["padrao_arquivo"]
    prefixo = padrao.split("{")[0].strip()  # "Ranking Waze"
    cols = fonte["colunas"]
    abas = fonte["abas_periodo"]

    meses = []
    for arquivo in sorted(pasta.glob("*.xlsx")):
        if arquivo.name.startswith("~"):
            continue
        nome = arquivo.stem
        m = re.search(
            re.escape(prefixo) + r"\s+([A-Za-zçÇãÃéÉêÊíÍóÓôÔ]+)\s+(\d{4})",
            nome,
        )
        if not m:
            continue
        mes_idx = _mes_para_indice(m.group(1))
        ano = int(m.group(2))
        if mes_idx is None:
            continue

        for periodo in abas:
            try:
                df = pd.read_excel(arquivo, sheet_name=periodo)
            except Exception:
                continue
            reg = pd.DataFrame()
            reg["_rua"] = df[cols["rua"]].fillna("Desconhecida").astype(str).str.strip()
            reg["_valor"] = pd.to_numeric(df[cols["valor"]], errors="coerce").fillna(0)
            reg = reg[reg["_rua"] != "Desconhecida"]
            meses.append({
                "ano": ano,
                "mes": mes_idx,
                "periodo": periodo,
                "registros": reg,
                "arquivo": arquivo.name,
            })

    if not meses:
        raise ValueError(f"Nenhum arquivo mensal reconhecido em {pasta}")

    return {
        "tipo": "ranking_mensal",
        "meses": meses,
        "diag": {
            "arquivos": sorted({m["arquivo"] for m in meses}),
            "blocos_mes_periodo": len(meses),
        },
    }
