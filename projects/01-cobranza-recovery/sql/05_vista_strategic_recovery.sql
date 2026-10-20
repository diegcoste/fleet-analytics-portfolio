-- =====================================================================
-- 05 · Lista operativa para Recovery de campo
-- Una fila por contrato con lo que el operador necesita en sitio:
-- segmento, band, última posición GPS y contactos aplanados.
-- Requiere: 01_params_y_base.sql
-- =====================================================================

CREATE OR REPLACE TEMP VIEW strategic_recovery AS
WITH hoy AS (
  SELECT b.*
  FROM sr_base b
  JOIN sr_params p ON b.business_date = p.fecha_final
  WHERE b.bucket >= 1
),
gps AS (
  SELECT vin, business_date, lat, lon, geofence_location_type, days_since_end_location
  FROM lakehouse.silver.gps_location
),
contacto AS (
  -- contacts: ARRAY<STRUCT<type STRING, value STRING, is_primary BOOLEAN>>
  SELECT
    contract_number,
    filter(contacts, x -> x.type = 'phone' AND x.is_primary)[0].value     AS telefono_principal,
    filter(contacts, x -> x.type = 'phone' AND NOT x.is_primary)[0].value AS telefono_alterno,
    filter(contacts, x -> x.type = 'reference')[0].value                  AS referencia
  FROM lakehouse.silver.contract_contacts
)
SELECT
  h.contract_number,
  h.vin,
  h.recovery_region,
  h.municipality,
  h.band,
  h.dpd,
  h.bucket,
  CASE
    WHEN h.bucket BETWEEN 1 AND 2  THEN 'RETENER'
    WHEN h.bucket = 3              THEN 'REACTIVAR'
    WHEN h.bucket BETWEEN 4 AND 10 THEN 'REDEFINIR R / R'
    WHEN h.bucket >= 11            THEN 'LEGAL'
  END                                         AS segmento,
  g.lat,
  g.lon,
  coalesce(g.geofence_location_type, 'NOT IN GEOFENCE') AS ubicacion,
  g.days_since_end_location                   AS dias_sin_reportar,
  CASE WHEN g.vin IS NULL THEN 'SIN GPS'
       WHEN g.days_since_end_location > 14 THEN 'GPS DESACTUALIZADO'
       ELSE 'GPS OK' END                      AS estado_gps,
  c.telefono_principal,
  c.telefono_alterno,
  c.referencia
FROM hoy h
LEFT JOIN gps g
  ON g.vin = h.vin
 AND g.business_date = h.business_date        -- en el ON para no romper el LEFT JOIN
LEFT JOIN contacto c
  ON c.contract_number = h.contract_number
WHERE h.band IS NOT NULL                      -- regla: sin band y > 28 días → fuera
  AND NOT EXISTS (                            -- excluye contratos ya en gestión legal formal
    SELECT 1 FROM lakehouse.silver.legal_cases lc
    WHERE lc.vin = h.vin AND lc.status_case <=> 'ACTIVE'
  );

SELECT * FROM strategic_recovery ORDER BY recovery_region, bucket DESC, dpd DESC;
