-- =====================================================================
-- 04 · Nuevos discoveries con columnas no exploradas
-- Requiere: 01_vistas_base.sql
-- Fecha de corte fija para que el resultado sea reproducible
-- =====================================================================

CREATE OR REPLACE TEMP VIEW p AS SELECT DATE '2026-10-08' AS fecha_corte;

-- 10.1 ¿"Sin multas" o "sin consultar"?
SELECT
  u.vehicle_state,
  count(*) AS unidades,
  sum(CASE WHEN m.stock_vehicles_id IS NOT NULL THEN 1 ELSE 0 END)                                              AS con_multas,
  sum(CASE WHEN m.stock_vehicles_id IS NULL AND datediff(p.fecha_corte, u.last_violation_check) <= 90 THEN 1 ELSE 0 END) AS consultada_reciente_sin_multas,
  sum(CASE WHEN m.stock_vehicles_id IS NULL AND datediff(p.fecha_corte, u.last_violation_check) >  90 THEN 1 ELSE 0 END) AS consulta_vieja_sin_multas,
  sum(CASE WHEN m.stock_vehicles_id IS NULL AND u.last_violation_check IS NULL THEN 1 ELSE 0 END)               AS nunca_consultada
FROM v_unidades u
CROSS JOIN p
LEFT JOIN (SELECT DISTINCT stock_vehicles_id FROM v_multas) m USING (stock_vehicles_id)
GROUP BY u.vehicle_state
ORDER BY nunca_consultada DESC;

-- 10.2 Unidades fuera de flota (baja o transferidas) con multas sin pagar
SELECT
  CASE WHEN fecha_baja IS NOT NULL THEN 'baja' ELSE 'transferida' END AS situacion,
  count(DISTINCT stock_vehicles_id) AS unidades,
  count(*)                          AS multas_unpaid,
  round(sum(monto), 2)              AS monto_unpaid
FROM v_multas
WHERE status_multa = 'unpaid'
  AND (fecha_baja IS NOT NULL OR transferred_to IS NOT NULL)
GROUP BY 1;

-- 10.3 Antigüedad de la deuda abierta por responsable
SELECT
  responsable,
  CASE
    WHEN datediff(p.fecha_corte, violation_date) <= 30  THEN '0-30'
    WHEN datediff(p.fecha_corte, violation_date) <= 90  THEN '31-90'
    WHEN datediff(p.fecha_corte, violation_date) <= 180 THEN '91-180'
    WHEN datediff(p.fecha_corte, violation_date) <= 365 THEN '181-365'
    ELSE '365+'
  END                   AS antiguedad,
  count(*)              AS multas,
  round(sum(monto), 2)  AS monto
FROM v_multas_resp CROSS JOIN p
WHERE status_multa = 'unpaid'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 10.5 Concentración: ¿la deuda está repartida o en pocos autos? (curva de Pareto)
WITH por_unidad AS (
  SELECT stock_vehicles_id, sum(monto) AS deuda
  FROM v_multas WHERE status_multa = 'unpaid'
  GROUP BY 1
),
rank AS (
  SELECT *,
         row_number() OVER (ORDER BY deuda DESC)                          AS rn,
         sum(deuda) OVER (ORDER BY deuda DESC) / sum(deuda) OVER ()       AS pct_acum
  FROM por_unidad
)
SELECT
  min(CASE WHEN pct_acum >= 0.5 THEN rn END) AS unidades_para_50pct_deuda,
  min(CASE WHEN pct_acum >= 0.8 THEN rn END) AS unidades_para_80pct_deuda,
  count(*)                                   AS unidades_con_deuda
FROM rank;

-- 10.7 ¿A cuántos días de entregado recibe su primera multa el cliente actual?
SELECT
  percentile_approx(dias, 0.5) AS mediana_dias,
  percentile_approx(dias, 0.9) AS p90_dias
FROM (
  SELECT stock_vehicles_id, datediff(min(violation_date), max(ultima_entrega)) AS dias
  FROM v_multas_resp
  WHERE responsable = 'cliente_actual'
  GROUP BY 1
);

-- 10.11 Rezago de captura: update_history como fecha aproximada de carga
--   update_history: array<struct<field STRING, date TIMESTAMP, user STRING>>
WITH eventos AS (
  SELECT s.stock_vehicles_id, cast(h.date AS DATE) AS fecha_evento
  FROM lakehouse.silver.fleet_stock_vehicles s
  LATERAL VIEW explode(s.update_history) t AS h
  WHERE h.field = 'violations'
)
SELECT
  percentile_approx(datediff(e.fecha_evento, m.violation_date), 0.5) AS mediana_dias_rezago,
  percentile_approx(datediff(e.fecha_evento, m.violation_date), 0.9) AS p90_dias_rezago
FROM v_multas m
JOIN eventos e
  ON e.stock_vehicles_id = m.stock_vehicles_id
 AND e.fecha_evento >= m.violation_date;
