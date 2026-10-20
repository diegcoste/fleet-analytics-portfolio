-- =====================================================================
-- 03 · Matriz de transición de buckets entre dos snapshots
-- Filas:    bucket_anterior (2..10, '11+')
-- Columnas: bucket_actual   (2..10, '11+', salidas, recuperaciones)
-- Valor:    número de contratos
-- Requiere: 01_params_y_base.sql
-- =====================================================================

CREATE OR REPLACE TEMP VIEW sr_transicion_buckets AS
WITH snap AS (
  SELECT b.contract_number, b.business_date, b.bucket
  FROM sr_base b
  CROSS JOIN sr_params p
  WHERE b.business_date IN (p.fecha_inicial, p.fecha_final)
),
ini AS (SELECT contract_number, bucket FROM snap, sr_params p WHERE business_date = p.fecha_inicial),
fin AS (SELECT contract_number, bucket FROM snap, sr_params p WHERE business_date = p.fecha_final),
pares AS (
  SELECT
    CASE WHEN i.bucket >= 11 THEN '11+' ELSE cast(i.bucket AS STRING) END AS bucket_anterior,
    CASE
      WHEN f.contract_number IS NULL THEN 'recuperaciones'   -- salió de cartera
      WHEN f.bucket IN (0, 1)        THEN 'salidas'          -- se puso al corriente
      WHEN f.bucket >= 11            THEN '11+'
      ELSE cast(f.bucket AS STRING)
    END AS bucket_actual
  FROM ini i
  LEFT JOIN fin f ON f.contract_number = i.contract_number
  WHERE i.bucket >= 2
)
SELECT *
FROM pares
PIVOT (
  count(*) FOR bucket_actual IN (
    '2', '3', '4', '5', '6', '7', '8', '9', '10', '11+', 'salidas', 'recuperaciones'
  )
);

SELECT *
FROM sr_transicion_buckets
ORDER BY CASE WHEN bucket_anterior = '11+' THEN 99 ELSE int(bucket_anterior) END;
