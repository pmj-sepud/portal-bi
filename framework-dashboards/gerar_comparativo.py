# -*- coding: utf-8 -*-
"""
gerar_comparativo.py — Gera o data-payload dos dashboards COMPARATIVOS do Waze
(mesma arquitetura do comparador "Acidentes Bombeiros UMO": comparar duas vias
A x B, com graficos borboleta por Ano/Mes/Dia/Periodo/Tipo).

Le a planilha-fonte (configurada no config/<id>.json) e reescreve apenas o
<script id="data-payload"> da pagina do Portal — a interface nao e tocada.

Uso:
    python gerar_comparativo.py acidentes_waze
"""
import sys, os, re, json, unicodedata
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("[ERRO] pandas nao encontrado. Execute: pip install pandas openpyxl")
    sys.exit(1)

AQUI = Path(__file__).resolve().parent               # framework-dashboards/
PORTAL = AQUI.parent                                 # portal-bi/
RAIZ = PORTAL.parent                                 # projeto/
CONFIG_DIR = AQUI / "config"

# config id -> pagina do Portal (comparativo)
DESTINO = {
    "acidentes_waze": "dashboards/waze/acidentes/index.html",
    "buracos":        "dashboards/waze/buracos/index.html",
    "alagamentos":    "dashboards/waze/alagamentos/index.html",
}

DOWS = ['Sem Registro', 'Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
TURNOS = ['Madrugada (00-06h)', 'Manhã (06-12h)', 'Tarde (12-18h)', 'Noite (18-24h)', 'Sem Registro']
SUBTIPO_PT = {
    'ACCIDENT_MINOR': 'Leve', 'ACCIDENT_MAJOR': 'Grave', 'ACCIDENT': 'Acidente',
}


def _turno(h):
    if pd.isna(h):
        return 4
    h = int(h)
    return 0 if h < 6 else 1 if h < 12 else 2 if h < 18 else 3


def _norm(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def gerar(config_id: str) -> dict:
    cfg = json.loads((CONFIG_DIR / f"{config_id}.json").read_text(encoding='utf-8'))
    fonte = cfg['fonte']
    xlsx = RAIZ / fonte['base'] / fonte['arquivo']
    if not xlsx.exists():
        raise FileNotFoundError(f"Planilha nao encontrada: {xlsx}")
    print(f"[INFO] Lendo: {xlsx}")
    df = pd.read_excel(xlsx, sheet_name=fonte.get('aba', 0))

    cols = fonte['colunas']
    c_data = cols['data']
    c_rua = cols['rua']
    c_hora = cols.get('hora')
    c_lat = cols.get('lat')
    c_lng = cols.get('lng')

    # detecta colunas opcionais (day_of_week, subtype) por nome aproximado
    c_dow = next((c for c in df.columns if _norm(c) in ('day_of_week', 'dia_semana', 'diadasemana')), None)
    c_sub = next((c for c in df.columns if _norm(c) in ('subtype', 'subtipo')), None)

    dt = pd.to_datetime(df[c_data], errors='coerce')
    df = df[dt.notna()].copy()
    dt = dt[dt.notna()]
    df['_ano'] = dt.dt.year.astype(int)
    df['_mes'] = dt.dt.month.astype(int)
    # dia da semana: usa a coluna do Waze (1=Dom..7=Sab) se existir; senao deriva
    if c_dow:
        df['_dow'] = pd.to_numeric(df[c_dow], errors='coerce').fillna(0).astype(int).clip(0, 7)
    else:
        df['_dow'] = (dt.dt.dayofweek.add(2) % 7).replace(0, 7).astype(int)  # Dom=1..Sab=7
    df['_turno'] = (df[c_hora].apply(_turno) if c_hora else 4)

    # ruas (indice estavel por nome)
    ruas = sorted([str(x) for x in df[c_rua].dropna().unique()])
    rua_idx = {r: i for i, r in enumerate(ruas)}

    # tipos (subtype) — humanizado; se nao houver, uma unica categoria
    if c_sub:
        def sub_label(v):
            if pd.isna(v) or str(v).strip() == '':
                return 'Não especificado'
            return SUBTIPO_PT.get(str(v), str(v).replace('_', ' ').title())
        df['_tipoL'] = df[c_sub].apply(sub_label)
        tipos = sorted(df['_tipoL'].unique().tolist())
    else:
        df['_tipoL'] = 'Registro'
        tipos = ['Registro']
    tipo_idx = {t: i for i, t in enumerate(tipos)}

    anos = sorted(df['_ano'].unique().tolist())

    # coordenadas (opcionais) para o mapa de dispersao
    tem_coord = bool(c_lat and c_lng and c_lat in df.columns and c_lng in df.columns)
    lat_s = pd.to_numeric(df[c_lat], errors='coerce') if tem_coord else None
    lng_s = pd.to_numeric(df[c_lng], errors='coerce') if tem_coord else None

    # registros: "ano,mes,dow,turno,ruaIdx,tipoIdx" + coords paralelas
    recs, coords = [], []
    it = zip(df['_ano'], df['_mes'], df['_dow'], df['_turno'], df[c_rua].astype(str), df['_tipoL'],
             (lat_s if tem_coord else [None] * len(df)), (lng_s if tem_coord else [None] * len(df)))
    for a, m, d, t, ru, tp, la, ln in it:
        ri = rua_idx.get(str(ru), -1)
        if ri < 0:
            continue
        recs.append(f"{a},{m},{d},{t},{ri},{tipo_idx[tp]}")
        if tem_coord and pd.notna(la) and pd.notna(ln):
            coords.append([round(float(la), 5), round(float(ln), 5)])
        else:
            coords.append(None)
    data_str = "|".join(recs)

    payload = {
        "ruas": ruas,
        "tipos": tipos,
        "sexos": [],       # nao ha vitimas/sexo no Waze — serie unica
        "destinos": [],
        "dows": DOWS,
        "turnos": TURNOS,
        "anos": anos,
        "data": data_str,
        "coords": coords,  # [lat,lng] por registro (ou null) — mapa de dispersao
    }
    return {"payload": payload, "n": len(recs), "ruas": len(ruas), "tipos": tipos, "anos": anos,
            "coords": sum(1 for c in coords if c)}


def injetar(config_id: str, payload: dict) -> Path:
    destino = PORTAL / DESTINO[config_id]
    html = destino.read_text(encoding='utf-8')
    novo = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    padrao = re.compile(r'(<script type="application/json" id="data-payload">).*?(</script>)', re.S)
    html2, n = padrao.subn(lambda m: m.group(1) + novo + m.group(2), html)
    if n != 1:
        raise RuntimeError(f"data-payload nao encontrado (ou duplicado): {n} ocorrencias em {destino}")
    destino.write_text(html2, encoding='utf-8')
    return destino


def contar_embedded(config_id: str) -> int:
    """Conta os registros embutidos no data-payload da página do Portal (auditoria)."""
    destino = PORTAL / DESTINO[config_id]
    html = destino.read_text(encoding='utf-8')
    m = re.search(r'id="data-payload">(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError(f"data-payload nao encontrado em {destino}")
    d = json.loads(m.group(1))
    return (d['data'].count('|') + 1) if d.get('data') else 0


def executar(config_id: str, log=None) -> dict:
    """Gera + injeta + AUDITA (gerador == embutido). Usado pela automação oficial."""
    def _log(msg):
        (log(msg) if log else print(msg))
    r = gerar(config_id)
    injetar(config_id, r["payload"])
    emb = contar_embedded(config_id)
    _log(f"  Registros informados pelo gerador : {r['n']}")
    _log(f"  Registros embutidos no dashboard  : {emb}")
    if emb != r["n"]:
        raise RuntimeError(f"DIVERGENCIA NA AUDITORIA: gerador={r['n']} != embutido={emb}")
    _log("  [OK] Correspondencia 100% (gerador == dashboard)")
    return {"n": r["n"], "ruas": r["ruas"], "anos": r["anos"], "portal": DESTINO[config_id]}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in DESTINO:
        print("Uso: python gerar_comparativo.py <" + "|".join(DESTINO) + ">")
        return 1
    cid = sys.argv[1]
    r = gerar(cid)
    destino = injetar(cid, r["payload"])
    print(f"[OK] {cid}: {r['n']:,} registros | {r['ruas']} vias | anos {r['anos']} | tipos {r['tipos']}".replace(",", "."))
    print(f"[OK] data-payload injetado em: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
