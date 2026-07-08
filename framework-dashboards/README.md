# Framework de Geração de Dashboards — Portal de BI Joinville

Um único código Python gera qualquer dashboard Waze a partir de um arquivo de
configuração. Separa **dados**, **processamento** e **renderização**.

## Estrutura

```
framework-dashboards/
├── gerar.py                 # ponto de entrada (CLI)
├── geradores/
│   ├── carregar_planilha.py # camada de DADOS  (lê xlsx, não transforma)
│   ├── processador.py       # camada de PROCESSAMENTO (KPIs, agregações)
│   ├── exportador_html.py   # camada de RENDERIZAÇÃO (template único)
│   └── dashboard_base.py    # ORQUESTRADOR + auditoria automática
├── config/
│   ├── alagamentos.json
│   ├── buracos.json
│   ├── ranqueamento.json
│   └── alertas.json         # bloqueado (fonte incompleta)
└── saida/                   # HTML gerado (não versionado)
```

## Uso

```bash
python gerar.py                       # gera alagamentos + buracos + ranqueamento
python gerar.py alagamentos           # gera apenas um
python -m geradores.dashboard_base buracos
```

Cada geração roda o pipeline completo **e** a auditoria
`Planilha → Python → JSON → HTML`, que só aprova com 100% de correspondência
(total de registros e distribuição por ano/mês idênticos à planilha).

## Adicionar um novo dashboard

Crie `config/<nome>.json`. Nenhuma linha de código nova é necessária.

Campos principais:

| Campo | Descrição |
|-------|-----------|
| `titulo`, `subtitulo` | cabeçalho do painel |
| `html_saida` | nome do arquivo gerado |
| `cor` | paleta (`primaria`, `escura`, `clara`, `accent`) |
| `fonte.tipo` | `"eventos"` (1 linha por ocorrência) ou `"ranking_mensal"` |
| `fonte.base` | pasta da planilha, relativa à raiz do projeto |
| `fonte.colunas` | mapeia papéis (`data`, `hora`, `rua`, `lat`, `lng`…) para os nomes reais das colunas |
| `kpis` | lista de indicadores (cada um aponta para uma métrica calculada) |
| `graficos`, `filtros` | opções de exibição |
| `bloqueado` | se `true`, o dashboard não é regenerado (ex.: fonte incompleta) |

## Regras de integridade

- As planilhas de origem **nunca** são alteradas (somente leitura).
- A única exclusão permitida é a de linhas **sem data válida** — contabilizada e
  reportada no diagnóstico.
- As agregações reproduzem as dos dashboards originais (contagem por mês/ano,
  período do dia, ranking de vias). Nenhum registro é omitido além do acima.
