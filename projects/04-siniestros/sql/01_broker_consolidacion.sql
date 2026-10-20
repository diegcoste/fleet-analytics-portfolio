-- =====================================================================
-- 01 · Consolidación de aseguradoras y match con la app
-- Requiere: notebooks/carga_brokers.py  (crea excel_broker_sinister_raw)
-- =====================================================================

-- Un registro por VIN con la regla de prioridad:
--   1) si existe un ABIERTO → gana el ABIERTO, y entre abiertos el más antiguo
--   2) si no              → el más reciente
CREATE OR REPLACE TEMP VIEW excel_broker_sinister_history AS
SELECT * EXCEPT (rn)
FROM (
  SELECT
    *,
    row_number() OVER (
      PARTITION BY SERIE
      ORDER BY
        CASE WHEN ESTATUS = 'ABIERTO' THEN 0 ELSE 1 END,
        CASE WHEN ESTATUS = 'ABIERTO' THEN FECSINIESTRO END ASC,
        FECSINIESTRO DESC
    ) AS rn
  FROM excel_broker_sinister_raw
  WHERE SERIE IS NOT NULL AND SERIE <> ''
)
WHERE rn = 1;

-- Siniestros registrados en la app
CREATE OR REPLACE TEMP VIEW adm_sinister AS
SELECT
  regexp_replace(upper(vin), '\\s+', '') AS vin_norm,
  sinister_id,
  sinister_status,
  sinister_type,
  created_at
FROM lakehouse.silver.fleet_sinisters;

-- Match: siniestros que existen en broker y en la app
CREATE OR REPLACE TEMP VIEW broker_con_match_adm_sinister AS
SELECT
  b.*,
  a.sinister_id,
  a.sinister_status,
  date_format(b.FECSINIESTRO, 'yyyy-MM') AS month_sinister
FROM excel_broker_sinister_history b
JOIN adm_sinister a
  ON a.vin_norm = b.SERIE;

-- Anti-join: el broker lo reporta y la app no lo tiene
CREATE OR REPLACE TEMP VIEW broker_sin_match_adm AS
SELECT b.*
FROM excel_broker_sinister_history b
LEFT ANTI JOIN adm_sinister a
  ON a.vin_norm = b.SERIE;

-- Resumen en una fila
SELECT
  (SELECT count(*) FROM excel_broker_sinister_raw)     AS registros_broker,
  (SELECT count(*) FROM excel_broker_sinister_history) AS vins_unicos_broker,
  (SELECT count(*) FROM broker_con_match_adm_sinister) AS con_match_app,
  (SELECT count(*) FROM broker_sin_match_adm)          AS sin_match_app;
