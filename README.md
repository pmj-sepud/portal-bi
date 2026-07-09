# Portal Inteligente de Business Intelligence — Prefeitura de Joinville

Portal corporativo que centraliza os dashboards de BI da Prefeitura de Joinville
(SEPUR / UMO). Site estático, publicado no GitHub Pages, com **home institucional**,
**Design System único** e um **framework em Python** que gera dashboards a partir
de configuração.

🔗 **Produção:** https://pmj-sepud.github.io/portal-bi/

---

## 1. Visão geral

| Camada | O que é | Onde vive |
|--------|---------|-----------|
| **Home (app-shell)** | Landing institucional: hero, busca em tempo real, favoritos, filtro por categoria, tema claro/escuro | `index.html`, `assets/css/portal.css`, `assets/js/portal.js`, `assets/js/catalog.js` |
| **Chrome dos dashboards** | Barra superior única (voltar, breadcrumb, relógio) + rodapé em torno de cada painel | `assets/css/dashboard.css`, `assets/js/main.js` |
| **Design System** | Componentes visuais únicos (header, filtros, KPI, gráficos, ranking, rodapé) | `assets/css/bi-dashboard-system.css` |
| **Dashboards** | 11 painéis em 7 categorias, com dados embutidos (HTML autossuficiente) | `dashboards/**/index.html` |
| **Framework** | Gera dashboards Waze a partir de config + audita a correspondência com a planilha | `framework-dashboards/` |
| **Reskin** | Overrides de interface que padronizam os dashboards de código próprio | `framework-dashboards/reskin/` |

---

## 2. Estrutura de pastas

```
portal-bi/
├── index.html                      # Home (app-shell institucional)
├── assets/
│   ├── css/
│   │   ├── portal.css              # App-shell da home (sidebar, hero, cards, dark mode)
│   │   ├── bi-dashboard-system.css # Design System dos dashboards (referência: Acidentes Bombeiros)
│   │   ├── style.css               # Sub-portais (Waze, Inventário)
│   │   └── dashboard.css           # Chrome comum das páginas de dashboard
│   ├── js/
│   │   ├── catalog.js              # Catálogo (fonte única de dados da home)
│   │   ├── portal.js               # Motor da home (busca, favoritos, tema, contadores)
│   │   └── main.js                 # Relógio do chrome dos dashboards
│   └── images/                     # Logos (Prefeitura + Secretaria)
├── dashboards/
│   ├── acidentes/                  # Referência oficial de interface (não alterar)
│   ├── equipamentos/  inventario/  processos/  radares/  transporte/
│   └── waze/                       # sub-portal + 5 painéis
└── framework-dashboards/
    ├── gerar.py                    # CLI: gera dashboards a partir das configs
    ├── geradores/                  # carregar_planilha · processador · exportador_html · dashboard_base
    ├── config/                     # 1 JSON por dashboard + _paleta_institucional.json
    └── reskin/                     # overrides CSS dos dashboards bespoke + inject.py
```

---

## 3. Design System

A referência oficial de interface é o dashboard **Acidentes Bombeiros UMO**. Toda a
linguagem visual (tipografia DM Sans/DM Mono, cards KPI, cards de gráfico, barra de
filtros, ranking, rodapé, sombras, raios, hover) está em
`assets/css/bi-dashboard-system.css`. A identidade de cada categoria muda **apenas**
pela cor, através das variáveis `--acc-*`.

### Paleta institucional (`framework-dashboards/config/_paleta_institucional.json`)

| Categoria | Cor | Principal |
|-----------|-----|-----------|
| Acidentes Bombeiros | Vermelho | `#dc2626` |
| Equipamentos SEPUR | Verde | `#16a34a` |
| Inventário UMO | Roxo | `#7c3aed` |
| Processos SEI UMO | Azul | `#2563eb` |
| Transporte Público UMO | Azul petróleo | `#0f766e` |
| Radares | Laranja | `#ea580c` |
| Waze UMO | Âmbar | `#d97706` |

Todos os tons compartilham saturação/luminosidade (padrão 900/600/400).

---

## 4. Como funciona o framework

Pipeline em três camadas, orquestrado por `dashboard_base.py`, com **auditoria
automática** ao final:

```
Planilha  →  carregar_planilha  →  processador  →  exportador_html  →  HTML
                                                                        │
                                                        auditoria: Planilha ↔ JSON ↔ HTML (100%)
```

- **carregar_planilha.py** — lê os `.xlsx` (fonte `eventos` = 1 linha por ocorrência,
  ou `ranking_mensal` = vários arquivos/abas). Só lê; nunca transforma.
- **processador.py** — calcula KPIs e agregações (mês/ano, período do dia, ranking de
  vias). Nenhum registro é descartado além de linhas sem data válida (reportadas).
- **exportador_html.py** — renderiza no Design System (inlina o CSS canônico).
- **dashboard_base.py** — orquestra e audita (relê a planilha de forma independente e
  compara total + distribuição ano/mês; só aprova com 100%).

### Regenerar os dashboards Waze

```bash
cd framework-dashboards
python gerar.py                    # gera alagamentos + buracos + ranqueamento + acidentes_waze
python gerar.py buracos            # gera apenas um
```

Depois integre as saídas ao portal (embute head+body na página do painel):
o script de integração usado é o mesmo padrão dos demais (ver histórico do repo).

---

## 5. Como criar um NOVO dashboard (via framework)

1. Coloque a planilha na pasta de origem.
2. Crie `framework-dashboards/config/<nome>.json`:

```json
{
  "id": "meu_dashboard",
  "titulo": "Meu Dashboard — Joinville",
  "subtitulo": "Descrição curta",
  "html_saida": "meu_dashboard.html",
  "icone": "📊",
  "cor": { "primaria": "#2563eb", "escura": "#1e3a8a", "clara": "#60a5fa", "accent": "#f5a623" },
  "fonte": {
    "tipo": "eventos",
    "base": "caminho/relativo/à/pasta",
    "arquivo": "planilha.xlsx",
    "aba": "Sheet1",
    "colunas": { "data": "data", "hora": "hora", "rua": "rua", "lat": "latitude", "lng": "longitude" }
  },
  "kpis": [ { "label": "Total", "metrica": "total", "formato": "int", "icone": "📈" } ],
  "graficos": { "ranking_ruas_top": 15 },
  "filtros": ["ano", "mes", "periodo"]
}
```

3. `python gerar.py meu_dashboard` — gera e audita. Nenhuma linha de código nova.

> Fonte incompleta? Marque `"bloqueado": true` na config para impedir a regeneração
> (é o caso de `alertas.json`, cuja planilha atual só tem um snapshot de 74 registros).

---

## 6. Como adicionar uma CATEGORIA ao portal (home)

Edite **apenas** `assets/js/catalog.js` e acrescente um objeto em `categorias`:

```js
{
  id: "nova",
  nome: "Nova Categoria",
  cor: "#0f766e",
  descricao: "…",
  href: "dashboards/nova/",
  registros: 1234,
  bases: 1,
  atualizacao: "2026-07-08",
  updating: false,
  keywords: ["palavra", "chave"],
  icone: '<path d="…"/>'   // SVG inline (viewBox 0 0 24 24)
}
```

A home renderiza o card, o item na sidebar, o chip de filtro, os contadores e o badge
de status automaticamente. **Status automático:** sem `registros` ⇒ 🔴 pendente;
`updating: true` ⇒ 🟡 atualizando; caso contrário ⇒ 🟢 atualizado.

---

## 7. Dashboards de código próprio (reskin)

Painéis não gerados pelo framework (Processos, Transporte, Equipamentos, Inventário,
Alertas) são padronizados por um override de interface, **sem alterar dados, KPIs,
gráficos, filtros ou JS**. Os overrides estão em `framework-dashboards/reskin/` e são
reaplicáveis:

```bash
cd framework-dashboards
python reskin/inject.py dashboards/processos/index.html reskin/processos.css
```

---

## 8. Como publicar no GitHub Pages

O portal é servido diretamente da raiz de `portal-bi/` na branch `main`.

```bash
git add -A
git commit -m "mensagem"
git push origin main
```

No repositório: **Settings → Pages → Deploy from branch → `main` / root**.
Como todos os caminhos são relativos, funciona em `usuario.github.io/portal-bi/`
sem ajustes.

---

## 9. Qualidade

- **Acessibilidade:** skip-link, `aria-label`/roles, foco visível (`:focus-visible`),
  navegação por teclado (atalho `/` foca a busca, `Esc` fecha o menu), `aria-live` nos
  resultados, contraste adequado em ambos os temas.
- **Performance:** SVGs inline (sem requisições de imagem), imagens com `loading="lazy"`,
  scripts com `defer`, CSS compartilhado, catálogo único (sem HTML duplicado).
- **Tema claro/escuro:** alternância persistida em `localStorage`, aplicada antes da
  pintura (sem flash), respeitando `prefers-color-scheme`.
- **Dados:** dashboards Waze auditados 1:1 com a planilha; reskins não tocam em dados.

---

## 10. Créditos

Prefeitura Municipal de Joinville · Secretaria de Pesquisa e Planejamento Urbano (SEPUR)
· Unidade de Mobilidade (UMO). Sistema de Business Intelligence — versão 2.0.0 (2026).
