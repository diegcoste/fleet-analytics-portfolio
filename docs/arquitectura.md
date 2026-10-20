# 🏗️ Arquitectura de datos

## Capas

| Capa | Contenido | Grano | Quién escribe |
|---|---|---|---|
| **Bronze** | Ingesta cruda: app operativa, GPS, CSV de aseguradoras, ticketera, proveedor de taller | Como llega | Data Engineering |
| **Silver** | Tablas limpias por entidad. Campos anidados (`ARRAY<STRUCT>`, `STRUCT`) se conservan | 1 fila por vehículo / contrato / evento | Data Engineering |
| **Gold** | Cartera diaria (`portfolio_overview`), scores de riesgo, dimensiones (`dim_calendario`) | 1 fila por contrato × `business_date` | Data / Risk |
| **Temp views** | Lógica analítica de cada proyecto, parametrizada por fechas | Depende del análisis | Fleet Analytics (yo) |

## Por qué *temp views* y no tablas

En la mayoría de los proyectos la regla de negocio todavía se estaba definiendo con el área usuaria. Las temp views permiten:

1. Iterar la lógica sin crear deuda en el catálogo.
2. Cambiar el rango de análisis con un solo `params` CTE.
3. Promover a tabla/vista persistente solo cuando la regla está firmada por el área.

```sql
WITH params AS (
  SELECT DATE '2026-09-01' AS fecha_inicial,
         DATE '2026-09-29' AS fecha_final
)
SELECT ...
FROM lakehouse.gold.portfolio_overview p
CROSS JOIN params
WHERE p.business_date BETWEEN params.fecha_inicial AND params.fecha_final
```

## Tablas fuente (genéricas)

| Tabla | Descripción | Campos relevantes |
|---|---|---|
| `lakehouse.silver.fleet_stock_vehicles` | Una fila por vehículo con todo su historial embebido | `vin`, `vehicle_state`, `category`, `sub_category`, `step STRUCT`, `delivered_date ARRAY<STRING>`, `violations ARRAY<STRUCT<folio, violationDate, status, amount, _id>>`, `car_plates STRUCT`, `update_history`, `last_violation_check`, `country` |
| `lakehouse.silver.fleet_readmissions` | Regresos de unidades a la empresa | `stock_vehicle_id`, `readmission_date`, `readmission_reason`, `contract_number` |
| `lakehouse.gold.portfolio_overview` | Cartera diaria por contrato | `business_date`, `contract_number`, `vin`, `dpd`, `bucket`, `vehicle_state`, `category` |
| `lakehouse.silver.gps_location` | Última posición por día | `vin`, `business_date`, `geofence_location_type`, `days_since_end_location`, `lat`, `lon` |
| `lakehouse.risk.contract_scores` | Score semanal de riesgo | `contract_number`, `week_date`, `score`, `band` |
| `lakehouse.dm.dim_calendario` | Calendario con días hábiles (LFT art. 74) | `fecha`, `es_habil`, `semana_iso` |

## Consumo

- **Tableau Cloud** conectado a Databricks como fuente única de verdad (SSOT).
- **Google Sheets** alimentado por un export plano (`DBX_DATA`) que se reemplaza in-place; todas las fórmulas del dashboard leen de ahí.
- **HTML autocontenido** para presentaciones ejecutivas y dashboards comerciales que se comparten por liga.
- **Listas operativas** (CSV) con calendario de entrega acordado: diario para Cobranza, semanal para Recovery.

## Convenciones

- Normalización de llaves: `upper(trim(x))` y `regexp_replace(x, '\\s+', '')` para VIN/serie.
- Fechas: `try_to_date` / `try_to_timestamp` para que un valor corrupto devuelva `NULL` en lugar de romper el job.
- Zona horaria: análisis en **UTC** cuando el dato se guarda a medianoche UTC (si no, el día de la semana se recorre).
- Universo explícito: `country = 'Mexico'` cuando aplica, para excluir otras operaciones.
- `business_date` de joins a tablas diarias va en el `ON`, no en el `WHERE`, para preservar la semántica del `LEFT JOIN`.
