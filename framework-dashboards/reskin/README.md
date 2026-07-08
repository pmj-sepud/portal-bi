# Reskin institucional dos dashboards bespoke

Overrides de interface (CSS) que padronizam os dashboards de código próprio
(não gerados pelo framework) ao Design System institucional, aplicando a cor da
categoria e o tema claro, **sem alterar dados, KPIs, gráficos, filtros ou JS**.

Cada arquivo é injetado como `<style id="bi-reskin">` antes de `</head>` na
página correspondente do portal:

| Arquivo                       | Dashboard                    | Cor        |
|-------------------------------|------------------------------|------------|
| processos.css                 | Processos SEI UMO            | Azul       |
| transporte.css                | Transporte Público UMO       | Petróleo   |
| equipamentos.css              | Equipamentos SEPUR          | Verde      |
| inventario_computadores.css   | Inventário · Computadores   | Roxo       |
| inventario_ippuj.css          | Inventário · CPUs IPPUJ     | Roxo       |
| radares.css                   | Radares (placeholder)       | Laranja    |

## Reaplicar (após regenerar um dashboard bespoke)

    python inject.py dashboards/processos/index.html reskin/processos.css

Observação: os dashboards Waze usam o próprio template do framework (já no
Design System) e não precisam de reskin.
