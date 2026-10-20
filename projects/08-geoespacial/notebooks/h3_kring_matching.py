# Databricks notebook source
# MAGIC %md
# MAGIC # Asignación vehículo → ubicación con H3 + k-ring
# MAGIC Funciones H3 nativas de Databricks SQL (`h3_longlatash3`, `h3_kring`). Resolución 9 ≈ 0.1 km² por celda.

# COMMAND ----------

RES = 9
K = 1
FECHA = "2026-09-15"

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TEMP VIEW ubicaciones_ring AS
SELECT
  u.location_id,
  u.location_type,                 -- PARK / WORKSHOP / DEPOT
  u.lat AS u_lat,
  u.lon AS u_lon,
  explode(h3_kring(h3_longlatash3(u.lon, u.lat, {RES}), {K})) AS cell
FROM lakehouse.silver.fleet_locations u
""")

spark.sql(f"""
CREATE OR REPLACE TEMP VIEW vehiculos_celda AS
SELECT
  g.vin,
  g.lat,
  g.lon,
  h3_longlatash3(g.lon, g.lat, {RES}) AS cell
FROM lakehouse.silver.gps_location g
WHERE g.business_date = DATE '{FECHA}'
  AND g.lat IS NOT NULL AND g.lon IS NOT NULL
""")

# COMMAND ----------

# Haversine en km para desempatar cuando una celda cae en el anillo de varias ubicaciones
asignacion = spark.sql("""
WITH candidatos AS (
  SELECT
    v.vin, r.location_id, r.location_type,
    2 * 6371 * asin(sqrt(
      pow(sin(radians(r.u_lat - v.lat) / 2), 2) +
      cos(radians(v.lat)) * cos(radians(r.u_lat)) * pow(sin(radians(r.u_lon - v.lon) / 2), 2)
    )) AS dist_km
  FROM vehiculos_celda v
  JOIN ubicaciones_ring r ON r.cell = v.cell
)
SELECT v.vin,
       c.location_id,
       coalesce(c.location_type, 'NOT IN LOCATION') AS location_type,
       round(c.dist_km, 3)                          AS dist_km
FROM vehiculos_celda v
LEFT JOIN (
  SELECT *, row_number() OVER (PARTITION BY vin ORDER BY dist_km) AS rn FROM candidatos
) c ON c.vin = v.vin AND c.rn = 1
""")
asignacion.createOrReplaceTempView("vehiculo_ubicacion")
display(asignacion.groupBy("location_type").count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Comparación: match exacto vs k-ring
# MAGIC Cuántas asignaciones recupera el anillo que el match exacto perdía.

# COMMAND ----------

display(spark.sql(f"""
WITH exacto AS (
  SELECT DISTINCT v.vin
  FROM vehiculos_celda v
  JOIN lakehouse.silver.fleet_locations u
    ON h3_longlatash3(u.lon, u.lat, {RES}) = v.cell
)
SELECT
  (SELECT count(*) FROM exacto)                                                AS asignados_match_exacto,
  (SELECT count(*) FROM vehiculo_ubicacion WHERE location_id IS NOT NULL)      AS asignados_kring,
  (SELECT count(*) FROM vehiculo_ubicacion WHERE location_id IS NOT NULL)
    - (SELECT count(*) FROM exacto)                                            AS recuperados_por_kring
"""))
