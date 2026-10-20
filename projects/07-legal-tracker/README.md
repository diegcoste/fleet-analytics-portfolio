# 07 · Legal Tracker

> Tablero operativo para el área Legal: universo de casos, backlog, entradas, salidas, recuperaciones, antigüedad y ubicación GPS de las unidades. Construido como prototipo HTML y llevado a **Tableau** con el design system del equipo.

## Proceso del proyecto

Cada tarea con entregable y criterio de salida explícitos ([plan completo](docs/plan_proyecto.md)):

```mermaid
flowchart LR
  A[Discovery con Legal] --> B[Levantamiento de<br/>fuentes y campos]
  B --> C[Universo y reglas<br/>firmadas por el área]
  C --> D[Cruce NUC × cartera<br/>por VIN]
  D --> E[Prototipo HTML<br/>iteraciones rápidas]
  E --> F[Tableau Cloud<br/>con design system]
  F --> G[Validación con<br/>usuario real]
```

## Universo legal

Un contrato entra al universo si **está en categoría legal** en la cartera, **o** tiene un número de carpeta de investigación (NUC) activo y la unidad no es elegible para venta:

```sql
CREATE OR REPLACE TEMP VIEW universe_legal AS
WITH pf AS (
  SELECT * FROM lakehouse.gold.portfolio_overview
  WHERE business_date = (SELECT max(business_date) FROM lakehouse.gold.portfolio_overview)
),
nuc AS (SELECT * FROM lakehouse.silver.legal_manual_nuc)
SELECT pf.*, nuc.* EXCEPT (vin, contract_number)
FROM pf
LEFT JOIN nuc ON nuc.vin = pf.vin
WHERE pf.category = 'legal'
   OR (nuc.status_nuc IS TRUE AND pf.is_eligible_for_sale IS FALSE);
```

## KPIs del tablero

`Total en universo` · `Con NUC fuera de categoría legal` · `En categoría legal` · `Backlog` · `Entradas` · `Salidas` · `Recuperaciones` · `Cumplimiento de metas por trámite`

Vistas: flujo del periodo, colas de pendientes, antigüedad, mapa GPS y unidades sin GPS por ciudad.

## Tableau: paginación con visibilidad dinámica

Un dashboard de tamaño fijo con varias "páginas" en el área central, manteniendo siempre visibles los KPIs, el sidebar y el footer. Implementado con un parámetro entero y **visibilidad de zona dinámica**, incluyendo filtros flotantes que aparecen solo en su página. Guía paso a paso: [`docs/tableau_paginacion.md`](docs/tableau_paginacion.md).
