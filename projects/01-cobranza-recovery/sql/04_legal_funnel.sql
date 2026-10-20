-- =====================================================================
-- 04 · Funnel hacia Legal: snapshot inicial vs snapshot final
-- Grano: región de recuperación × municipio
-- Requiere: 01_params_y_base.sql
-- =====================================================================

CREATE OR REPLACE TEMP VIEW sr_legal_funnel_ciudad AS
WITH ini AS (
  SELECT b.contract_number, b.recovery_region, b.municipality, b.bucket
  FROM sr_base b JOIN sr_params p ON b.business_date = p.fecha_inicial
),
fin AS (
  SELECT b.contract_number, b.recovery_region, b.municipality, b.bucket
  FROM sr_base b JOIN sr_params p ON b.business_date = p.fecha_final
),
j AS (
  SELECT
    coalesce(i.recovery_region, f.recovery_region) AS recovery_region,
    coalesce(i.municipality,    f.municipality)    AS municipality,
    i.contract_number AS c_ini, i.bucket AS b_ini,
    f.contract_number AS c_fin, f.bucket AS b_fin
  FROM ini i
  FULL OUTER JOIN fin f ON f.contract_number = i.contract_number
)
SELECT
  recovery_region,
  municipality,
  count(DISTINCT CASE WHEN b_ini BETWEEN 2 AND 10 THEN c_ini END)                                       AS backlog_inicial,
  count(DISTINCT CASE WHEN NOT coalesce(b_ini BETWEEN 2 AND 10, false) AND b_fin BETWEEN 2 AND 10 THEN c_fin END) AS entradas,
  count(DISTINCT CASE WHEN b_ini BETWEEN 2 AND 10 AND NOT coalesce(b_fin BETWEEN 2 AND 10, false) THEN c_ini END) AS salidas,
  count(DISTINCT CASE WHEN b_ini BETWEEN 2 AND 10 AND b_fin BETWEEN 2 AND 10 THEN c_ini END)            AS backlog_final,
  count(DISTINCT CASE WHEN b_ini BETWEEN 2 AND 10 AND b_fin >= 11 THEN c_ini END)                       AS transiciono_a_legal
FROM j
GROUP BY recovery_region, municipality;

-- Agregado por región (suma de municipios)
CREATE OR REPLACE TEMP VIEW sr_legal_funnel_recovery AS
SELECT
  recovery_region,
  sum(backlog_inicial)     AS backlog_inicial,
  sum(entradas)            AS entradas,
  sum(salidas)             AS salidas,
  sum(backlog_final)       AS backlog_final,
  sum(transiciono_a_legal) AS transiciono_a_legal,
  round(try_divide(sum(transiciono_a_legal), sum(backlog_inicial)) * 100, 2) AS pct_a_legal
FROM sr_legal_funnel_ciudad
GROUP BY recovery_region;

SELECT * FROM sr_legal_funnel_recovery ORDER BY backlog_inicial DESC;
