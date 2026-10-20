# 05 · Talleres — Discoveries críticos

> Diagnóstico de la operación de talleres cruzando **4 sistemas** por VIN: app operativa (estatus "Taller"), proveedor de taller (órdenes correctivas/preventivas), ticketera y facturas XML. Cada hallazgo se traduce en **cashflow inmovilizado**: conductores activos sin cobro, stock sin liberar y unidades sin vender.

## Hilo conductor

Los hallazgos comparten una misma raíz: **los sistemas se actualizan por separado, sin una llave que los sincronice, sin SLAs que reflejen la operación real y sin un dueño del proceso.**

## Discoveries

| # | Discovery | Lo que mostró el dato (cualitativo) |
|---|---|---|
| D1 | **Backlog en estatus "Taller"** | Cientos de unidades detenidas con mediana de ~6 meses; casi ningún movimiento de estatus con dueño identificable |
| D2 | **Ticketera: resolución y SLA** | Incumplimiento de SLA prácticamente total — **por diseño**: el SLA mide respuesta en horas, no resolución |
| D3 | **Match de 3 sistemas** | Solo un porcentaje de un dígito de los VINs con trabajo abierto existe en los 3 sistemas; la mayoría vive en uno solo |
| D3b | **Aging del desajuste** | Días en desajuste × tarifa diaria → exposición estimada de cashflow |
| D4 | **Facturas vs órdenes** | Muchas menos facturas XML que servicios completados; ningún mes concilia al 100 % |
| D5 | **SLA de correctivos del proveedor** | SLA en horas contra una realidad de semanas |
| D6 | **Correctivos no completados** | Cientos de órdenes abiertas concentradas en un solo proveedor |

## Regla del match (D3)

| Tipo de cliente | Debe aparecer en |
|---|---|
| Cliente **activo** con la unidad en taller | App **y** proveedor **y** ticketera |
| Cliente **inactivo** (unidad de stock) | Al menos app **y** proveedor |

## Selección de estadístico por métrica

| Métrica | Elegido | Por qué |
|---|---|---|
| Aging en estatus Taller | **Mediana** | Un pico de ingresos reciente deflacta la media |
| Tiempo entre cambios de estatus | **P90** | La mediana (~2 días) oculta los tickets abandonados |
| Tiempo al primer comentario | **P90** | La mediana ≈ 0 es el comentario automático |
| Tiempo de resolución de ticket | **Mediana** | La media se infla por pocos casos lentos |
| Propuesta de SLA nuevo | **P90 de resolución** | Ancla la meta en lo que la operación sí logra |

## Planes de acción (D3, ejemplo)

**Plan A — raíz:** VIN obligatorio como llave en los 3 sistemas · evento canónico de entrada/salida de taller que sincroniza los 3 · máquina de estados con transiciones válidas · una fuente de verdad orquestadora · KPI diario de match con alerta < 95 % · dueño y SLA por sistema.

**Plan B — contener:** cola diaria de conciliación segmentada por sistema faltante y tipo de cliente, con acción recomendada y prioridad (P1 clientes activos / pérdida potencial · P2 stock).

## Archivos

| Archivo | Contenido |
|---|---|
| [`notebooks/match_3_sistemas.py`](notebooks/match_3_sistemas.py) | D3: match por VIN, regla por tipo de cliente, cola de conciliación |
| [`notebooks/aging_cashflow.py`](notebooks/aging_cashflow.py) | D3b: aging del desajuste y exposición con resolución defensiva de columnas |
| [`notebooks/kpi_cards_html.py`](notebooks/kpi_cards_html.py) | Celda autocontenida de KPI cards + Plotly con `displayHTML` |
