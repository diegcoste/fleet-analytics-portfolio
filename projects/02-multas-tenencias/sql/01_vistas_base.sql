-- =====================================================================
-- 01 · Vistas base de multas
-- Sin limpieza: los valores se leen como vienen. Solo se convierten tipos.
-- Tipos de la fuente:
--   violations     → array<struct<folio, violationDate:timestamp, status, amount:double, _id>>
--   delivered_date → array<string>
--   car_plates, step, discharged_data → struct
-- =====================================================================

-- Todo el notebook corre en UTC: violationDate se guarda a medianoche UTC
-- y en hora local el día se recorre (afecta día de la semana y bordes de mes).
SET TIME ZONE 'UTC';

-- ---------------------------------------------------------------------
-- v_unidades: una fila por unidad + última readmisión
-- ---------------------------------------------------------------------
CREATE OR REPLACE TEMP VIEW v_unidades AS
SELECT
  s.stock_vehicles_id,
  s.vin,
  s.vehicle_state,
  s.brand,
  s.model,
  s.year,
  s.category,
  s.sub_category,
  s.status                                       AS status_unidad,
  s.car_plates.plates                            AS placas,
  s.step.stepName                                AS step_name,
  try_cast(s.reception_date AS DATE)             AS reception_date,
  r.ultima_readmission                           AS readmission_date,
  r.motivo_ultima_readmission,
  cast(s.last_violation_check AS DATE)           AS last_violation_check,
  size(s.delivered_date)                         AS num_entregas,
  try_cast(array_min(s.delivered_date) AS DATE)  AS primera_entrega,
  try_cast(array_max(s.delivered_date) AS DATE)  AS ultima_entrega,
  s.platform,
  s.is_blocked,
  s.gps_installed,
  s.last_driver_id,
  s.discharged_data.date                         AS fecha_baja,
  s.discharged_data.reason                       AS motivo_baja,
  s.transferred_to
FROM lakehouse.silver.fleet_stock_vehicles s
LEFT JOIN (
  SELECT
    stock_vehicle_id,
    cast(max(readmission_date) AS DATE)           AS ultima_readmission,
    max_by(readmission_reason, readmission_date)  AS motivo_ultima_readmission
  FROM lakehouse.silver.fleet_readmissions
  GROUP BY stock_vehicle_id
) r ON r.stock_vehicle_id = s.stock_vehicles_id
WHERE s.country = 'Mexico';

-- ---------------------------------------------------------------------
-- v_multas: una fila por multa (explode) + atributos de la unidad
-- ---------------------------------------------------------------------
CREATE OR REPLACE TEMP VIEW v_multas AS
SELECT
  u.*,
  m.folio,
  cast(m.violationDate AS DATE) AS violation_date,
  m.status                      AS status_multa,
  m.amount                      AS monto,
  m._id                         AS violation_id
FROM lakehouse.silver.fleet_stock_vehicles s
JOIN v_unidades u
  ON u.stock_vehicles_id = s.stock_vehicles_id
LATERAL VIEW explode(s.violations) t AS m;

-- ---------------------------------------------------------------------
-- v_multas_resp: responsable con última entrega y última readmisión
-- (versión simple; la completa reconstruye todas las ventanas)
-- ---------------------------------------------------------------------
CREATE OR REPLACE TEMP VIEW v_multas_resp AS
SELECT
  *,
  CASE
    WHEN violation_date < reception_date                                             THEN 'antes_recepcion'
    WHEN ultima_entrega IS NULL                                                      THEN 'sin_cliente'
    WHEN violation_date < primera_entrega                                            THEN 'sin_cliente'
    WHEN readmission_date >= ultima_entrega AND violation_date >= readmission_date   THEN 'sin_cliente'
    WHEN readmission_date >= ultima_entrega AND violation_date >= ultima_entrega     THEN 'cliente_anterior'
    WHEN violation_date >= ultima_entrega                                            THEN 'cliente_actual'
    ELSE 'cliente_anterior'
  END AS responsable
FROM v_multas;
