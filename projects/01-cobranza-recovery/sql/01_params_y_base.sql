-- =====================================================================
-- 01 · Parámetros y base de cartera
-- Proyecto: Cobranza & Strategic Recovery
-- Motor:    Databricks SQL / Spark SQL
-- Salida:   temp views (no se crean tablas)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Parámetros: único lugar donde se cambia el periodo de análisis
-- ---------------------------------------------------------------------
CREATE OR REPLACE TEMP VIEW sr_params AS
SELECT
  DATE '2026-09-01' AS fecha_inicial,
  DATE '2026-09-29' AS fecha_final;

-- ---------------------------------------------------------------------
-- Band vigente por contrato: última semana calificada
-- ---------------------------------------------------------------------
CREATE OR REPLACE TEMP VIEW sr_band_vigente AS
SELECT
  contract_number,
  max(week_date)              AS week_date,
  max_by(score, week_date)    AS score,
  max_by(band,  week_date)    AS band_score
FROM lakehouse.risk.contract_scores
GROUP BY contract_number;

-- ---------------------------------------------------------------------
-- Base diaria en el rango + región + band final
-- ---------------------------------------------------------------------
CREATE OR REPLACE TEMP VIEW sr_base AS
SELECT
  p.business_date,
  p.contract_number,
  p.vin,
  p.vehicle_state,
  p.municipality,
  p.dpd,
  p.bucket,
  p.contract_start_date,
  CASE
    WHEN p.vehicle_state IN ('cdmx', 'mer', 'pbe', 'qro')         THEN 'REGION_CENTRO'
    WHEN p.vehicle_state IN ('mty', 'sal', 'torr')                THEN 'REGION_NORESTE'
    WHEN p.vehicle_state IN ('tij', 'mxli', 'her', 'chi')         THEN 'REGION_NOROESTE'
    WHEN p.vehicle_state IN ('gdl', 'ptv', 'leo', 'ags', 'slp')   THEN 'REGION_OCCIDENTE'
    ELSE NULL                                                     -- ciudad nueva → salta en QA
  END AS recovery_region,
  CASE
    WHEN datediff(p.business_date, p.contract_start_date) <= 28 THEN 'NUEVO'
    ELSE b.band_score
  END AS band
FROM lakehouse.gold.portfolio_overview p
CROSS JOIN sr_params prm
LEFT JOIN sr_band_vigente b
  ON b.contract_number = p.contract_number
WHERE p.business_date BETWEEN prm.fecha_inicial AND prm.fecha_final
  AND p.country = 'Mexico';

-- ---------------------------------------------------------------------
-- QA: ciudades sin región y contratos fuera de lista por no tener band
-- ---------------------------------------------------------------------
SELECT 'vehicle_state sin región' AS chequeo, count(DISTINCT vehicle_state) AS n
FROM sr_base WHERE recovery_region IS NULL
UNION ALL
SELECT 'contratos > 28 días sin band', count(DISTINCT contract_number)
FROM sr_base WHERE band IS NULL;
