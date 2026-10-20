-- =====================================================================
-- 02 · Flujo semanal de contratos en buckets 2–5
-- Flujo Inicial + Entradas − Salidas = Flujo Final
-- Requiere: 01_params_y_base.sql
-- =====================================================================

CREATE OR REPLACE TEMP VIEW sr_flujo_semanal AS
WITH semanal AS (
  -- Una fila por contrato y semana: el bucket con el que cerró la semana
  SELECT
    contract_number,
    recovery_region,
    concat(year(business_date), '-', lpad(weekofyear(business_date), 2, '0')) AS year_week,
    max_by(bucket, business_date)                                            AS bucket_cierre
  FROM sr_base
  GROUP BY 1, 2, 3
),
con_lag AS (
  SELECT
    *,
    lag(bucket_cierre) OVER (PARTITION BY contract_number ORDER BY year_week) AS bucket_prev
  FROM semanal
),
flags AS (
  SELECT
    year_week,
    recovery_region,
    coalesce(bucket_prev   BETWEEN 2 AND 5, false) AS estaba,
    coalesce(bucket_cierre BETWEEN 2 AND 5, false) AS esta
  FROM con_lag
)
SELECT
  year_week,
  recovery_region,
  sum(CASE WHEN estaba             THEN 1 ELSE 0 END) AS flujo_inicial,
  sum(CASE WHEN esta AND NOT estaba THEN 1 ELSE 0 END) AS entradas,
  sum(CASE WHEN estaba AND NOT esta THEN 1 ELSE 0 END) AS salidas,
  sum(CASE WHEN esta               THEN 1 ELSE 0 END) AS flujo_final
FROM flags
GROUP BY year_week, recovery_region;

-- Control: la identidad del flujo debe cumplirse en todas las filas
SELECT *
FROM sr_flujo_semanal
WHERE flujo_final <> flujo_inicial + entradas - salidas;

-- Reporte
SELECT * FROM sr_flujo_semanal ORDER BY year_week, recovery_region;
