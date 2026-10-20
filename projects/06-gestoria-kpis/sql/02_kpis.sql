-- =====================================================================
-- 02 · KPIs con meta derivada de datos
-- Requiere: 01_tramites_con_habiles.sql
-- =====================================================================

-- ---------------------------------------------------------------------
-- KPI 1.1 · Tasa de completitud mensual
-- Derivación de la meta: P75 de las tasas de meses MADUROS
-- (solicitados hace > 3× el SLA más común; los recientes aún no cierran)
-- ---------------------------------------------------------------------
WITH mensual AS (
  SELECT
    trunc(fecha_solicitud, 'MM')                         AS mes,
    count(*)                                             AS solicitados,
    sum(CASE WHEN fecha_cierre IS NOT NULL THEN 1 END)   AS completados
  FROM tramites_con_habiles
  GROUP BY 1
),
maduros AS (
  SELECT *, completados / solicitados AS tasa
  FROM mensual
  WHERE mes < add_months(trunc(DATE '2026-05-01', 'MM'), -2)
)
SELECT round(percentile(tasa, 0.75) * 100, 1) AS meta_completitud_pct
FROM maduros;

-- KPI 1.1 · medición
SELECT
  trunc(fecha_solicitud, 'MM') AS mes,
  count(*)                     AS solicitados,
  round(try_divide(sum(CASE WHEN fecha_cierre IS NOT NULL THEN 1 ELSE 0 END), count(*)) * 100, 1) AS tasa_completitud
FROM tramites_con_habiles
GROUP BY 1
ORDER BY 1;

-- ---------------------------------------------------------------------
-- KPI 1.3 · Aging: umbral = 3 × SLA más común (moda)
-- ---------------------------------------------------------------------
WITH moda AS (
  SELECT sla_dias_habiles
  FROM tramites_con_habiles
  GROUP BY 1
  ORDER BY count(*) DESC
  LIMIT 1
)
SELECT
  m.sla_dias_habiles * 3                                                     AS umbral_dias_habiles,
  sum(CASE WHEN t.fecha_cierre IS NULL AND t.dias_habiles > m.sla_dias_habiles * 3 THEN 1 ELSE 0 END) AS tramites_sobre_umbral
FROM tramites_con_habiles t
CROSS JOIN moda m
GROUP BY m.sla_dias_habiles;

-- ---------------------------------------------------------------------
-- KPI 2.x · % en SLA del proveedor, global y por trámite × ciudad
-- Score agregado DESDE EL CASO (no promedio de porcentajes)
-- ---------------------------------------------------------------------
SELECT
  coalesce(tramite_type, 'TOTAL') AS tramite_type,
  coalesce(ciudad, 'TOTAL')       AS ciudad,
  count(*)                        AS completados,
  round(avg(CASE WHEN en_sla THEN 1.0 ELSE 0.0 END) * 100, 1) AS pct_en_sla
FROM tramites_con_habiles
WHERE fecha_cierre IS NOT NULL
GROUP BY ROLLUP (tramite_type, ciudad)
ORDER BY tramite_type, ciudad;

-- KPI 2.4 · Lista de escalamiento: trámites activos en breach
SELECT request_id, vin, ciudad, tramite_type, fecha_solicitud, dias_habiles, sla_dias_habiles,
       dias_habiles - sla_dias_habiles AS dias_excedidos
FROM tramites_con_habiles
WHERE breach_activo
ORDER BY dias_excedidos DESC;

-- ---------------------------------------------------------------------
-- KPI 5.2 · Desviación de costo vs tarifa de catálogo
-- ---------------------------------------------------------------------
SELECT
  trunc(fecha_solicitud, 'MM')                        AS mes,
  round(sum(cost), 0)                                 AS gasto,
  round(sum(cost - tarifa_catalogo), 0)               AS desviacion_vs_catalogo,
  sum(CASE WHEN cost > tarifa_catalogo THEN 1 ELSE 0 END) AS tramites_sobre_tarifa
FROM tramites_con_habiles
WHERE cost IS NOT NULL
GROUP BY 1
ORDER BY 1;
