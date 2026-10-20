-- =====================================================================
-- 03 · Export plano DBX_DATA (18 columnas) con hallazgo y flag de outlier
-- Alimenta el dashboard de Sheets: se reemplaza in-place en cada refresh.
-- Requiere: 02_gps_iqr.sql
-- =====================================================================

WITH bounds AS (
  SELECT ESTATUS, location_bucket,
         percentile(days_since_end_location, 0.25) AS q1,
         percentile(days_since_end_location, 0.75) AS q3
  FROM gps_adm_sinister
  GROUP BY 1, 2
),
global AS (
  SELECT percentile(days_since_end_location, 0.25) AS q1,
         percentile(days_since_end_location, 0.75) AS q3
  FROM gps_adm_sinister
),
base AS (
  SELECT
    g.*,
    datediff(DATE '2026-07-07', g.FECSINIESTRO) AS dias_desde_siniestro,
    CASE WHEN g.days_since_end_location > b.q3 + 1.5 * (b.q3 - b.q1) THEN 1 ELSE 0 END  AS outlier_segmento,
    CASE WHEN g.days_since_end_location > gl.q3 + 1.5 * (gl.q3 - gl.q1) THEN 1 ELSE 0 END AS outlier_global
  FROM gps_adm_sinister g
  LEFT JOIN bounds b ON b.ESTATUS = g.ESTATUS AND b.location_bucket = g.location_bucket
  CROSS JOIN global gl
)
SELECT
  SERIE                       AS vin,               -- A
  BROKER                      AS aseguradora,       -- B
  SINIESTRO                   AS siniestro,         -- C
  ESTATUS                     AS estatus,           -- D
  SUBESTATUS                  AS subestatus,        -- E
  TIPO                        AS tipo,              -- F
  sinister_status             AS estatus_app,       -- G
  month_sinister              AS mes_siniestro,     -- H
  FECSINIESTRO                AS fecha_siniestro,   -- I
  dias_desde_siniestro,                             -- J
  location_bucket             AS ubicacion,         -- K
  days_since_end_location     AS dias_en_ubicacion, -- L
  outlier_segmento,                                 -- M
  outlier_global,                                   -- N
  CASE                                              -- O
    WHEN ESTATUS = 'CERRADO' AND location_bucket = 'WORKSHOP'                                   THEN 1
    WHEN ESTATUS = 'CERRADO' AND location_bucket = 'NOT IN GEOFENCE'                            THEN 2
    WHEN ESTATUS = 'ABIERTO' AND location_bucket = 'PARK'                                       THEN 3
    WHEN ESTATUS = 'ABIERTO' AND location_bucket = 'WORKSHOP' AND SUBESTATUS = 'PERDIDATOTAL'   THEN 4
    WHEN ESTATUS = 'ABIERTO' AND location_bucket = 'WORKSHOP'
         AND SUBESTATUS IN ('VALUACION', 'REPARACION') AND dias_desde_siniestro > 30            THEN 5
    WHEN ESTATUS = 'ABIERTO' AND location_bucket = 'WORKSHOP'
         AND SUBESTATUS IN ('VALUACION', 'REPARACION') AND dias_desde_siniestro <= 30           THEN 6
    WHEN ESTATUS = 'ABIERTO' AND location_bucket IN ('NOT IN GEOFENCE', 'SIN GPS')
         AND SUBESTATUS = 'PERDIDATOTAL'                                                        THEN 7
  END                         AS hallazgo,
  CASE WHEN location_bucket = 'SIN GPS' THEN 'NO GPS' ELSE 'GPS' END AS tiene_gps,  -- P
  current_timestamp()         AS generado_en,       -- Q
  DATE '2026-07-07'           AS fecha_corte        -- R
FROM base;
