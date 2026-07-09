# Automação do Portal BI

Atualize qualquer dashboard **sem abrir terminal, VS Code ou Python**:
troque a planilha da pasta e dê **duplo clique** no `atualizar_dashboard.bat`.

Tudo funciona por **caminhos relativos** — o projeto pode ser copiado para
qualquer computador sem nenhum ajuste.

---

## O que acontece ao rodar um .BAT

```
1. Localiza a planilha da própria pasta
2. Executa o GERADOR OFICIAL do dashboard (nunca edita HTML à mão)
3. AUDITORIA: Planilha -> Gerador/Framework -> Dashboard
        divergência  =>  PARA e não publica nada
4. Copia o HTML gerado para o Portal BI (preservando a identidade visual)
5. Atualiza o Centro de Operações (catalog.js): registros, data, sincronização
6. git add + commit (mensagem automática) + push
7. Aguarda o GitHub Pages e confirma HTTP 200
8. Abre o dashboard publicado no navegador
9. Grava um log em  logs/<dashboard>_<data>_<hora>.log
```

Se a auditoria falhar, **nada é publicado** e o erro é mostrado com clareza.

---

## Onde estão os .BAT

| Pasta | Arquivo | Dashboard |
|---|---|---|
| `Dashboards HTML/Acidentes Bombeiros UMO/` | `atualizar_dashboard.bat` | Acidentes Bombeiros |
| `Dashboards HTML/Equipamentos SEPUR/` | `atualizar_dashboard.bat` | Equipamentos |
| `Dashboards HTML/Inventario UMO/` | `atualizar_dashboard.bat` | Inventário (CPUs IPPUJ) |
| `Dashboards HTML/Processos SEI UMO/` | `atualizar_dashboard.bat` | Processos SEI |
| `Dashboards HTML/Radares/` | `atualizar_dashboard.bat` | Radares |
| `Dashboards HTML/Transporte Publico UMO/` | `atualizar_dashboard.bat` | Transporte Público |
| `Dashboards HTML/Waze UMO/` | `atualizar_dashboard.bat` | Waze (4 painéis) |
| **raiz do projeto** | **`atualizar_tudo.bat`** | **todos**, com **um único** commit/push |

Todos os `.BAT` são **idênticos**; muda apenas o dashboard que atualizam.

---

## Arquivos da automação

```
portal-bi/automacao/
├── atualizar.py        # orquestrador de UM dashboard (chamado pelos .BAT)
├── atualizar_tudo.py   # todos em sequência, um único commit/push
├── registro.py         # mapa dos dashboards (única coisa que difere entre eles)
├── comum.py            # planilha, gerador, auditoria, portal, catálogo, git, Pages, log
└── README.md
```

Uso manual (opcional):

```bash
python atualizar.py processos
python atualizar.py waze --sem-publicar      # testa sem git/push
python atualizar_tudo.py --sem-navegador
```

---

## Tipos de dashboard

| Tipo | Como é gerado | Auditoria |
|---|---|---|
| `framework` | Framework BI (config JSON) — **Waze** | Estrita: planilha ↔ JSON ↔ HTML, distribuição por ano/mês |
| `bespoke` | Gerador oficial da pasta — Acidentes, Inventário, Processos, Transporte | Estrita: registros do gerador == registros embutidos no HTML |
| `manual` | **Equipamentos** — dados mantidos no próprio HTML (sem gerador) | O BAT apenas republica o painel |
| `placeholder` | **Radares** — ainda sem painel/dados | O BAT informa e encerra |

> **Waze · Alertas** está bloqueado no framework (planilha ainda parcial) e
> não é regenerado — o BAT do Waze avisa e segue com os demais painéis.

---

## Requisitos (uma vez por computador)

- **Python 3.8+** — marque *"Add Python to PATH"* na instalação.
- **Git** — com permissão de escrita no repositório do Portal.
- Bibliotecas dos geradores: `pandas`, `openpyxl` (`pip install pandas openpyxl`).

O BAT verifica Python e Git antes de começar e explica o que fazer se faltar.

---

## Mensagens de erro tratadas

- Python não instalado · Git não instalado · repositório ausente
- Planilha inexistente na pasta
- Gerador oficial ausente ou com erro
- **Divergência na auditoria** (para tudo, não publica)
- Erro no commit / push / GitHub

---

## Adicionar um novo dashboard à automação

1. Cadastre-o em `registro.py` (pasta, gerador, HTML gerado, página do Portal,
   reskin, painel do catálogo).
2. Copie um `.BAT` existente para a pasta nova e troque apenas `set "DASHBOARD=..."`.

Nada mais precisa mudar.
