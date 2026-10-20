# 06 · Gestoría — Framework de KPIs

> Sistema de medición para el proceso de **gestoría vehicular** (alta y baja de placas, tarjeta de circulación, tenencias/refrendos) dividiendo la responsabilidad entre el **equipo interno** (solicitar a tiempo, documentar, dar seguimiento) y el **proveedor de gestoría** (ejecutar el trámite dentro de SLA).

## Principio rector

> **Ninguna meta es un número inventado.** Cada KPI trae su query de derivación, su query principal y su gráfica — y la meta nunca se deriva del mismo periodo que se evalúa (sin lógica circular).

## 5 pilares · 15 KPIs

| Pilar | KPI | Meta y cómo se justifica |
|---|---|---|
| **1. Eficiencia interna** | Tasa de completitud | P75 de las tasas mensuales de **meses maduros** |
| | Aging de trámites abiertos | 0 trámites con > 3× el SLA más común (en días hábiles) |
| | % "esperando documentos" | Tope derivado del histórico estable |
| **2. SLA del proveedor** | % en SLA global / por trámite / por ciudad | Estándar contractual (cada trámite × ciudad tiene SLA y precio propios) |
| | Trámites activos en breach | 0 — lista de escalamiento en vivo |
| **3. Integridad documental** | % con placa · % con tarjeta de circulación | 100 % |
| | % con tenencia vigente | Margen pequeño que cubre la ventana activa de renovación |
| **4. Volumen** | Ratio de resolución mensual | P75 de meses maduros |
| | Distribución por ciudad / tipo | Monitoreo |
| **5. Costos** | Gasto mensual | Banda de ±5 % sobre el promedio |
| | Desviación vs tarifa de catálogo | Tope mensual de desviación |

## Lo técnico

- **Días hábiles exactos** con `dim_calendario` (descansos obligatorios LFT art. 74). Se precalcula una sola vez en `tramites_con_habiles` y todos los KPIs se unen contra esa vista → sin subqueries correlacionadas repetidas.
- **Score agregado desde el caso**: el score global se calcula sobre mediciones individuales, no promediando porcentajes de grupos (evita la paradoja de Simpson).
- **Universo documental** reconstruido desde campos JSON de la tabla de stock (`car_plates`, `circulation_card`, `tenancy`) con UNPIVOT, más `update_history` para eventos de gestoría.
- **Fix de `Decimal`**: Spark devuelve `ROUND/AVG/PERCENTILE` como `decimal.Decimal` en pandas y Matplotlib truena → *monkey-patch* global de `toPandas()`.
- **División segura** en PySpark: `F.when(den == 0, None).otherwise(num / den)`.

## Revisión crítica de una versión previa

Antes de la versión final se auditó un notebook existente y se corrigieron 7 problemas, entre ellos: denominador circular en un KPI, metas derivadas del P90 del mismo periodo medido, una meta sin justificación, un proxy incorrecto de completitud documental (adjunto en ticket ≠ documento vigente) y una variable definida dentro de un bloque `%skip`.

## Archivos

| Archivo | Contenido |
|---|---|
| [`sql/01_tramites_con_habiles.sql`](sql/01_tramites_con_habiles.sql) | Vista base con días hábiles vía acumulado del calendario |
| [`sql/02_kpis.sql`](sql/02_kpis.sql) | Derivación de metas + KPIs principales |
| [`notebooks/decimal_fix.py`](notebooks/decimal_fix.py) | Patch de `toPandas()` y plantilla de gráfica |
