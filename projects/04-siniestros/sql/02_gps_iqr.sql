-- =====================================================================
-- 02 · Ubicación GPS y medianas IQR por estatus × ubicación
-- Requiere: 01_broker_consolidacion.sql
-- =====================================================================

CREATE OR REPLACE TEMP VIEW gps_adm_sinister AS
SELECT
  m.*,
  CASE
    WHEN g.vin IS NULL
      OR (g.lat IS NULL AND g.lon IS NULL AND g.days_since_end_location IS NULL) THEN 'SIN GPS'
    ELSE coalesce(g.geofence_location_type, 'NOT IN GEOFENCE')
  END                         AS location_bucket,
  g.days_since_end_location
FROM broker_con_match_adm_sinister m
LEFT JOIN lakehouse.silver.gps_location g
  ON g.vin = m.SERIE
 AND g.business_date = DATE '2026-07-07';   -- fecha de corte en el ON: preserva el LEFT JOIN

-- Conteo + mediana sin outliers, por estatus y ubicación
WITH bounds AS (
  SELECT
    ESTATUS,
    location_bucket,
    percentile(days_since_end_location, 0.25) AS q1,
    percentile(days_since_end_location, 0.75) AS q3
  FROM gps_adm_sinister
  WHERE location_bucket <> 'SIN GPS'
  GROUP BY 1, 2
)
SELECT
  g.ESTATUS,
  g.location_bucket,
  count(*)                                                           AS unidades,
  percentile(
    CASE WHEN g.days_since_end_location
              BETWEEN b.q1 - 1.5 * (b.q3 - b.q1) AND b.q3 + 1.5 * (b.q3 - b.q1)
         THEN g.days_since_end_location END, 0.5)                    AS mediana_iqr_dias,
  sum(CASE WHEN g.days_since_end_location > b.q3 + 1.5 * (b.q3 - b.q1) THEN 1 ELSE 0 END) AS outliers
FROM gps_adm_sinister g
LEFT JOIN bounds b
  ON b.ESTATUS = g.ESTATUS AND b.location_bucket = g.location_bucket
GROUP BY g.ESTATUS, g.location_bucket
ORDER BY g.ESTATUS, unidades DESC;
