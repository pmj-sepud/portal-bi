"""
insights_helpers.py — Funções auxiliares de cálculo para os slides de
"Principais Insights" exibidos no Modo TV.

Cada gerador de dashboard (rodando como subprocess, em pasta própria) importa
este módulo via sys.path.insert() e usa `escrever_insights()` pra gravar um
`insights.json` ao lado do HTML que ele já produz. O orquestrador
(atualizar.py) depois lê esse arquivo e chama render_insights.renderizar().

Contrato do insights.json:
    { "titulo": str, "cor": "#rrggbb", "gerado_em": "YYYY-MM-DDTHH:MM",
      "linhas": [str, ...] }   # no máx. 5 linhas, texto já formatado/pronto
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def pct_share(count: int, total: int) -> float:
    """% que `count` representa de `total`. 0 se total for 0."""
    if not total:
        return 0.0
    return round(100 * count / total, 1)


def variacao_pct(atual: float, anterior: float) -> float | None:
    """Variação percentual de `anterior` pra `atual`. None se anterior for 0
    (variação não faz sentido / divisão por zero)."""
    if not anterior:
        return None
    return round(100 * (atual - anterior) / anterior, 1)


def mes_com_pico(serie: dict[str, int]) -> tuple[str, int]:
    """Recebe {rótulo_do_mês: valor} e devolve (rótulo, valor) do maior."""
    if not serie:
        return ("", 0)
    rotulo, valor = max(serie.items(), key=lambda kv: kv[1])
    return (rotulo, valor)


def top_categoria(contagens: dict[str, int]) -> tuple[str, int, float]:
    """Recebe {categoria: contagem} e devolve (nome, contagem, % do total)
    da categoria líder."""
    if not contagens:
        return ("", 0, 0.0)
    total = sum(contagens.values())
    nome, contagem = max(contagens.items(), key=lambda kv: kv[1])
    return (nome, contagem, pct_share(contagem, total))


def escrever_insights(pasta: Path, titulo: str, cor: str, linhas: list[str]) -> None:
    """Grava insights.json na pasta de saída do gerador. Trunca em 5 linhas.
    Nunca lança exceção — uma falha aqui não pode derrubar a publicação do
    dashboard principal."""
    try:
        dados = {
            "titulo": titulo,
            "cor": cor,
            "gerado_em": datetime.now().strftime("%Y-%m-%dT%H:%M"),
            "linhas": [str(l) for l in linhas[:5]],
        }
        (pasta / "insights.json").write_text(
            json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as e:  # pragma: no cover
        print(f"  AVISO: falha ao gravar insights.json: {e}")
