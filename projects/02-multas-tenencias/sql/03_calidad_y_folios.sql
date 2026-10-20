-- =====================================================================
-- 03 · Calidad de fechas, montos y folios
-- Requiere: 01_vistas_base.sql
-- =====================================================================

-- Fechas vacías, futuras o inverosímiles
SELECT
  count(*)                                                                      AS multas,
  sum(CASE WHEN violation_date IS NULL THEN 1 ELSE 0 END)                       AS sin_fecha_o_ilegible,
  sum(CASE WHEN violation_date > current_date() THEN 1 ELSE 0 END)              AS fecha_futura,
  sum(CASE WHEN year(violation_date) < cast(year AS INT) - 1 THEN 1 ELSE 0 END) AS antes_del_modelo_del_auto,
  sum(CASE WHEN violation_date < reception_date THEN 1 ELSE 0 END)              AS antes_de_recepcion
FROM v_multas;

-- Distribución de montos
SELECT
  count(*)                                         AS multas,
  sum(CASE WHEN monto IS NULL THEN 1 ELSE 0 END)   AS monto_nulo,
  sum(CASE WHEN monto = 0     THEN 1 ELSE 0 END)   AS monto_cero,
  sum(CASE WHEN monto < 0     THEN 1 ELSE 0 END)   AS monto_negativo,
  round(percentile_approx(monto, 0.5),  2)         AS monto_mediana,
  round(percentile_approx(monto, 0.95), 2)         AS monto_p95,
  round(max(monto), 2)                             AS monto_max
FROM v_multas;

-- Folios en más de una unidad
--  · misma fecha y mismo monto  → probable duplicado (monto inflado)
--  · fecha o monto distintos    → folio reutilizado (no sirve como llave única)
SELECT
  folio,
  count(DISTINCT stock_vehicles_id) AS unidades,
  count(DISTINCT violation_date)    AS fechas,
  count(DISTINCT monto)             AS montos,
  CASE WHEN count(DISTINCT violation_date) = 1 AND count(DISTINCT monto) = 1
       THEN 'misma multa en varios autos'
       ELSE 'folio reutilizado' END AS tipo
FROM v_multas
WHERE folio IS NOT NULL
GROUP BY folio
HAVING count(DISTINCT stock_vehicles_id) > 1
ORDER BY unidades DESC;

-- Monto potencialmente duplicado
SELECT tipo, count(*) AS folios, round(sum(monto_total - monto_una_vez), 2) AS monto_potencialmente_duplicado
FROM (
  SELECT folio, sum(monto) AS monto_total, max(monto) AS monto_una_vez,
         CASE WHEN count(DISTINCT violation_date) = 1 AND count(DISTINCT monto) = 1
              THEN 'misma multa en varios autos' ELSE 'folio reutilizado' END AS tipo
  FROM v_multas
  WHERE folio IS NOT NULL
  GROUP BY folio
  HAVING count(DISTINCT stock_vehicles_id) > 1
)
GROUP BY tipo;

-- Consistencia de la línea de tiempo de la unidad
SELECT 'Step Entregado sin fecha de entrega' AS chequeo, count(*) AS registros
FROM v_unidades WHERE step_name = 'Entregado' AND ultima_entrega IS NULL
UNION ALL
SELECT 'Primera entrega antes de reception_date', count(*)
FROM v_unidades WHERE primera_entrega < reception_date
UNION ALL
SELECT 'Entregas sin reception_date', count(*)
FROM v_unidades WHERE num_entregas > 0 AND reception_date IS NULL
UNION ALL
SELECT 'Readmisión posterior a hoy', count(*)
FROM v_unidades WHERE readmission_date > current_date()
UNION ALL
SELECT 'Readmisión sin entrega previa', count(*)
FROM v_unidades WHERE readmission_date IS NOT NULL AND primera_entrega IS NULL;
