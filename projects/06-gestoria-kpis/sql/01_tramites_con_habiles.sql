-- =====================================================================
-- 01 · Trámites con días hábiles exactos
-- Truco: un acumulado de días hábiles convierte "contar hábiles entre A y B"
-- en una resta de dos lookups por igualdad (sin subquery correlacionada).
-- =====================================================================

CREATE OR REPLACE TEMP VIEW cal_acum AS
SELECT
  fecha,
  es_habil,
  sum(CASE WHEN es_habil THEN 1 ELSE 0 END) OVER (ORDER BY fecha) AS habiles_acum
FROM lakehouse.dm.dim_calendario;

CREATE OR REPLACE TEMP VIEW tramites_con_habiles AS
WITH p AS (SELECT DATE '2026-05-01' AS fecha_corte),
t AS (
  SELECT
    s.request_id,
    s.vin,
    s.vehicle_state                                   AS ciudad,
    s.tramite_type,
    s.status,
    to_date(s.created_at)                             AS fecha_solicitud,
    to_date(s.completed_at)                           AS fecha_cierre,
    s.cost,
    c.sla_dias_habiles,
    c.tarifa_catalogo
  FROM lakehouse.silver.gestoria_requests s
  LEFT JOIN lakehouse.silver.gestoria_service_catalog c
    ON c.tramite_type = s.tramite_type AND c.ciudad = s.vehicle_state   -- SLA y precio por trámite × ciudad
)
SELECT
  t.*,
  coalesce(t.fecha_cierre, p.fecha_corte)                       AS fecha_fin_medicion,
  cf.habiles_acum - ci.habiles_acum                             AS dias_habiles,
  CASE WHEN t.fecha_cierre IS NOT NULL
       THEN (cf.habiles_acum - ci.habiles_acum) <= t.sla_dias_habiles END AS en_sla,
  t.fecha_cierre IS NULL
    AND (cf.habiles_acum - ci.habiles_acum) > t.sla_dias_habiles AS breach_activo
FROM t
CROSS JOIN p
JOIN cal_acum ci ON ci.fecha = t.fecha_solicitud
JOIN cal_acum cf ON cf.fecha = coalesce(t.fecha_cierre, p.fecha_corte);
