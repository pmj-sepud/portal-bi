"""
processador.py — Camada de PROCESSAMENTO.

Recebe os registros brutos de carregar_planilha e a configuração, e produz um
"pacote de dados" pronto para renderização: tabela de ruas, registros compactos,
agregações (por mês/ano, por período, ranking de ruas) e os KPIs declarados na
config. Não gera HTML e não lê arquivos — apenas transforma dados em memória.

Regra de ouro: as agregações reproduzem exatamente as dos dashboards originais
(contagem por mês/ano, distribuição por período do dia, ranking de ruas por
volume). Nenhum registro é descartado além das linhas sem data (feito na camada
de dados) — todo o restante é preservado 1:1.
"""

from collections import defaultdict, Counter

# Períodos do dia (faixas horárias) — convenção usada nos dashboards Waze.
PERIODOS = ["Madrugada", "Manhã", "Tarde", "Noite"]


def _periodo_idx(hora: int) -> int:
    if hora < 0:
        return -1
    if hora <= 5:
        return 0   # Madrugada 00–05
    if hora <= 11:
        return 1   # Manhã 06–11
    if hora <= 17:
        return 2   # Tarde 12–17
    return 3       # Noite 18–23


def processar(bruto: dict, config: dict) -> dict:
    if bruto["tipo"] == "eventos":
        return _processar_eventos(bruto, config)
    if bruto["tipo"] == "ranking_mensal":
        return _processar_ranking(bruto, config)
    raise ValueError(f"Tipo não suportado: {bruto['tipo']}")


# ---------------------------------------------------------------------------
# EVENTOS
# ---------------------------------------------------------------------------
def _processar_eventos(bruto: dict, config: dict) -> dict:
    df = bruto["registros"]
    tem_hora = bool((df["_hora"] >= 0).any())

    # Tabela de ruas (índice compacto) ordenada alfabeticamente para estabilidade.
    ruas = sorted(df["_rua"].unique().tolist())
    rua_idx = {r: i for i, r in enumerate(ruas)}

    registros = []          # [ano, mes, ruaIdx, periodoIdx, lat, lng]
    por_mes_ano = Counter()  # (ano, mes) -> n
    por_periodo = Counter()  # periodoIdx -> n
    por_rua = Counter()      # ruaIdx -> n
    por_ano = Counter()      # ano -> n

    for _, r in df.iterrows():
        d = r["_data"]
        ano, mes = int(d.year), int(d.month)
        ridx = rua_idx[r["_rua"]]
        pidx = _periodo_idx(int(r["_hora"])) if tem_hora else -1
        lat = round(float(r["_lat"]), 5) if r["_lat"] is not None and r["_lat"] == r["_lat"] else None
        lng = round(float(r["_lng"]), 5) if r["_lng"] is not None and r["_lng"] == r["_lng"] else None

        registros.append([ano, mes, ridx, pidx, lat, lng])
        por_mes_ano[(ano, mes)] += 1
        if pidx >= 0:
            por_periodo[pidx] += 1
        por_rua[ridx] += 1
        por_ano[ano] += 1

    total = len(registros)
    anos = sorted(por_ano.keys())

    # Série mensal completa (todos os 12 meses de cada ano, inclusive zeros).
    serie_mes_ano = {}
    for ano in anos:
        serie_mes_ano[str(ano)] = [por_mes_ano.get((ano, m), 0) for m in range(1, 13)]

    # Ranking de ruas (top N configurável, padrão 15).
    top_n = config.get("graficos", {}).get("ranking_ruas_top", 15)
    ranking = sorted(por_rua.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    ranking_ruas = [[ruas[i], n] for i, n in ranking]

    periodo_counts = [int(por_periodo.get(i, 0)) for i in range(4)]

    # Mês de pico (para KPI).
    if por_mes_ano:
        (pico_ano, pico_mes), pico_n = max(por_mes_ano.items(), key=lambda kv: kv[1])
    else:
        pico_ano = pico_mes = pico_n = 0

    metrics = {
        "total": total,
        "ruas_distintas": len(ruas),
        "anos_cobertos": len(anos),
        "periodo_min": f"{anos[0]}" if anos else "—",
        "periodo_max": f"{anos[-1]}" if anos else "—",
        "mes_pico": f"{_MES_ABR[pico_mes-1]}/{pico_ano}" if pico_n else "—",
        "mes_pico_valor": pico_n,
        "media_mensal": round(total / max(1, len(por_mes_ano)), 0),
        "rua_lider": ranking_ruas[0][0] if ranking_ruas else "—",
    }

    return {
        "tipo": "eventos",
        "tem_hora": tem_hora,
        "ruas": ruas,
        "registros": registros,
        "serie_mes_ano": serie_mes_ano,
        "anos": anos,
        "ranking_ruas": ranking_ruas,
        "periodo_counts": periodo_counts,
        "periodos_label": PERIODOS,
        "metrics": metrics,
        "kpis": _montar_kpis(config, metrics),
        "diag": bruto["diag"],
    }


# ---------------------------------------------------------------------------
# RANKING MENSAL
# ---------------------------------------------------------------------------
def _processar_ranking(bruto: dict, config: dict) -> dict:
    blocos = bruto["meses"]

    ruas_set = set()
    for b in blocos:
        ruas_set.update(b["registros"]["_rua"].tolist())
    ruas = sorted(ruas_set)
    rua_idx = {r: i for i, r in enumerate(ruas)}

    top_n = config.get("graficos", {}).get("ranking_ruas_top", 15)

    # dados["Mes_Ano"]["PERIODO"] = [[ruaIdx, valor], ...]  (ordenado por valor desc)
    dados = defaultdict(dict)
    meses_presentes = set()
    total_entradas = 0
    for b in blocos:
        chave = f"{_MES_FULL[b['mes']-1]}_{b['ano']}"
        meses_presentes.add((b["ano"], b["mes"]))
        pares = [
            [rua_idx[row["_rua"]], int(row["_valor"])]
            for _, row in b["registros"].iterrows()
        ]
        total_entradas += len(pares)
        pares.sort(key=lambda x: x[1], reverse=True)
        dados[chave][b["periodo"]] = pares[:top_n]

    meses_ordenados = sorted(meses_presentes)
    chaves_ordenadas = [f"{_MES_FULL[m-1]}_{a}" for a, m in meses_ordenados]

    # Rua líder global (maior delay acumulado somando todos os meses/períodos).
    acum = Counter()
    for b in blocos:
        for _, row in b["registros"].iterrows():
            acum[rua_idx[row["_rua"]]] += int(row["_valor"])
    rua_lider = ruas[max(acum, key=acum.get)] if acum else "—"

    metrics = {
        "meses_cobertos": len(meses_presentes),
        "ruas_distintas": len(ruas),
        "total_entradas": total_entradas,
        "periodo_min": f"{_MES_ABR[meses_ordenados[0][1]-1]}/{meses_ordenados[0][0]}" if meses_ordenados else "—",
        "periodo_max": f"{_MES_ABR[meses_ordenados[-1][1]-1]}/{meses_ordenados[-1][0]}" if meses_ordenados else "—",
        "rua_lider": rua_lider,
    }

    return {
        "tipo": "ranking_mensal",
        "ruas": ruas,
        "dados_ranking": dados,
        "chaves_mes": chaves_ordenadas,
        "periodos_ranking": config["fonte"]["abas_periodo"],
        "metrics": metrics,
        "kpis": _montar_kpis(config, metrics),
        "diag": bruto["diag"],
    }


# ---------------------------------------------------------------------------
# KPIs declarativos: a config aponta para uma métrica calculada acima.
# ---------------------------------------------------------------------------
def _montar_kpis(config: dict, metrics: dict) -> list:
    saida = []
    for kpi in config.get("kpis", []):
        valor = metrics.get(kpi["metrica"], "—")
        saida.append({
            "label": kpi["label"],
            "valor": valor,
            "formato": kpi.get("formato", "int"),
            "sufixo": kpi.get("sufixo", ""),
            "icone": kpi.get("icone", ""),
        })
    return saida


_MES_ABR = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
_MES_FULL = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
