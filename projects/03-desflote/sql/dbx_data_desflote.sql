-- =====================================================================
-- Export plano DBX_DATA_DESFLOTE
-- Una fila por unidad en proceso de desflote, con su estatus comercial,
-- oferta vigente, condición y fechas del funnel.
-- El Sheet se refresca reemplazando in-place esta salida.
-- =====================================================================

CREATE OR REPLACE TEMP VIEW desflote_universo AS
SELECT
  s.vin,
  s.vehicle_state,
  s.brand,
  s.model,
  s.year,
  s.category,
  s.sub_category,
  s.step.stepName                         AS step_name,
  s.olv_value,                                          -- valor de referencia de mercado
  s.market_valuation,
  s.repair_cost,
  s.condition_grade,                                    -- Buena / Media / Mala
  try_cast(s.defleet_assigned_date AS DATE) AS fecha_asignacion
FROM lakehouse.silver.fleet_stock_vehicles s
WHERE s.country = 'Mexico'
  AND (s.category = 'defleet' OR s.sub_category IN ('sold', 'for_sale', 'defleet_pending'));

-- Oferta vigente: autorizada > pendiente > la más reciente
CREATE OR REPLACE TEMP VIEW desflote_oferta_vigente AS
SELECT * EXCEPT (rn)
FROM (
  SELECT
    o.vin,
    o.buyer_alias,                                      -- comprador anonimizado
    o.offer_amount,
    o.offer_status,
    o.offer_date,
    row_number() OVER (
      PARTITION BY o.vin
      ORDER BY CASE o.offer_status WHEN 'authorized' THEN 0 WHEN 'pending' THEN 1 ELSE 2 END,
               o.offer_date DESC
    ) AS rn
  FROM lakehouse.silver.defleet_offers o
)
WHERE rn = 1;

SELECT
  u.*,
  o.buyer_alias,
  o.offer_amount,
  o.offer_status,
  o.offer_date,
  v.invoice_date,
  v.payment_date,
  v.sale_amount,
  CASE
    WHEN v.payment_date IS NOT NULL                        THEN 'Vendida / Pagada'
    WHEN v.invoice_date IS NOT NULL                        THEN 'Pendiente de pago'
    WHEN o.offer_status = 'authorized'                     THEN 'En proceso'
    WHEN u.sub_category IN ('recovery', 'legal')           THEN 'No disponible'
    ELSE 'Disponible'
  END                                                      AS estatus_comercial,
  u.olv_value * CASE u.condition_grade
                  WHEN 'Buena' THEN 0.80
                  WHEN 'Media' THEN 0.70
                  WHEN 'Mala'  THEN 0.35
                END                                        AS valor_por_condicion,
  datediff(v.payment_date, u.fecha_asignacion)             AS sla_venta_dias,
  date_format(u.fecha_asignacion, 'yyyy-MM')               AS mes_asignacion
FROM desflote_universo u
LEFT JOIN desflote_oferta_vigente o USING (vin)
LEFT JOIN lakehouse.silver.defleet_sales v USING (vin);
