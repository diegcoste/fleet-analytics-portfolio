-- =====================================================================
-- 02 · Inventario, completitud y cobertura por estado
-- Requiere: 01_vistas_base.sql
-- =====================================================================

-- 1. Inventario: el universo en una sola fila
SELECT
  (SELECT count(*)                           FROM v_unidades) AS unidades_flotilla,
  (SELECT count(DISTINCT vehicle_state)      FROM v_unidades) AS estados_flotilla,
  (SELECT count(*)                           FROM v_multas)   AS multas,
  (SELECT count(DISTINCT stock_vehicles_id)  FROM v_multas)   AS unidades_con_multa,
  (SELECT count(DISTINCT vehicle_state)      FROM v_multas)   AS estados_con_multa,
  (SELECT min(violation_date)                FROM v_multas)   AS primera_multa,
  (SELECT max(violation_date)                FROM v_multas)   AS ultima_multa,
  (SELECT round(sum(monto), 2)               FROM v_multas)   AS monto_total;

-- 2. Atributos: lo que trae violations vs lo que necesitaríamos
SELECT * FROM VALUES
  ('Folio de la multa',                 'folio',         '✅ Tenemos'),
  ('Fecha de la infracción',            'violationDate', '✅ Tenemos'),
  ('Estatus (pagada / pendiente)',      'status',        '✅ Tenemos'),
  ('Monto',                             'amount',        '✅ Tenemos'),
  ('Concepto / tipo de infracción',     '—',             '❌ No tenemos'),
  ('Autoridad / municipio emisor',      '—',             '❌ No tenemos'),
  ('Fecha de pago',                     '—',             '❌ No tenemos'),
  ('Fecha de captura',                  '—',             '❌ No tenemos'),
  ('Placa al momento de la infracción', '—',             '❌ No tenemos'),
  ('Ubicación de la infracción',        '—',             '❌ No tenemos'),
  ('Evidencia / documento',             '—',             '❌ No tenemos'),
  ('Quién pagó',                        '—',             '❌ No tenemos')
AS t(atributo, campo, estado);

-- 3. Completitud de campos clave (count(col) solo cuenta no nulos)
SELECT
  count(*)                                                    AS unidades,
  round(count(vin)                  / count(*) * 100, 2)      AS pct_vin,
  round(count(vehicle_state)        / count(*) * 100, 2)      AS pct_estado,
  round(count(placas)               / count(*) * 100, 2)      AS pct_placas,
  round(count(reception_date)       / count(*) * 100, 2)      AS pct_reception_date,
  round(count(ultima_entrega)       / count(*) * 100, 2)      AS pct_con_entrega,
  round(count(last_violation_check) / count(*) * 100, 2)      AS pct_last_violation_check
FROM v_unidades;

-- 4. Cobertura por estado: flotilla vs multas
--    Un estado con flotilla grande y 0 multas es un HUECO, no flotilla limpia.
SELECT
  u.vehicle_state,
  count(*)                                              AS unidades_flotilla,
  count(m.stock_vehicles_id)                            AS unidades_con_multa,
  round(count(m.stock_vehicles_id) / count(*) * 100, 2) AS pct_penetracion,
  coalesce(sum(m.multas), 0)                            AS multas,
  round(coalesce(sum(m.multas), 0) / count(*) * 100, 2) AS multas_x100_unidades,
  max(m.ultima_multa)                                   AS ultima_multa,
  CASE WHEN count(m.stock_vehicles_id) = 0 THEN '❌ Sin multas registradas' ELSE '' END AS alerta
FROM v_unidades u
LEFT JOIN (
  SELECT stock_vehicles_id, count(*) AS multas, max(violation_date) AS ultima_multa
  FROM v_multas
  GROUP BY stock_vehicles_id
) m ON m.stock_vehicles_id = u.stock_vehicles_id
GROUP BY u.vehicle_state
ORDER BY unidades_flotilla DESC;

-- 5. Huecos de carga: meses sin dato y meses desde la última carga
SELECT
  e.vehicle_state,
  e.primer_mes,
  e.ultimo_mes,
  int(months_between(e.ultimo_mes, e.primer_mes)) + 1                    AS meses_en_rango,
  e.meses_con_dato,
  int(months_between(e.ultimo_mes, e.primer_mes)) + 1 - e.meses_con_dato AS meses_sin_dato,
  int(months_between(g.ultimo_mes_global, e.ultimo_mes))                 AS meses_desde_ultimo_dato,
  CASE WHEN int(months_between(g.ultimo_mes_global, e.ultimo_mes)) >= 2
       THEN '⚠️ Dejó de cargar' ELSE '' END                              AS alerta
FROM (
  SELECT vehicle_state,
         min(trunc(violation_date, 'MM'))            AS primer_mes,
         max(trunc(violation_date, 'MM'))            AS ultimo_mes,
         count(DISTINCT trunc(violation_date, 'MM')) AS meses_con_dato
  FROM v_multas
  WHERE violation_date >= '2022-01-01'
  GROUP BY vehicle_state
) e
CROSS JOIN (SELECT max(trunc(violation_date, 'MM')) AS ultimo_mes_global FROM v_multas) g
ORDER BY meses_desde_ultimo_dato DESC, meses_sin_dato DESC;
