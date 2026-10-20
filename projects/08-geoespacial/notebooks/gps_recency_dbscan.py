# Databricks notebook source
# MAGIC %md
# MAGIC # Recencia de GPS × riesgo × atraso, y clusters con DBSCAN

# COMMAND ----------

import numpy as np
from pyspark.sql import functions as F
from sklearn.cluster import DBSCAN

FECHA = "2026-09-15"
UMBRAL_DIAS = 14

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Validación del umbral de recencia
# MAGIC Entre las unidades que dejaron de reportar, ¿a partir de cuántos días es "desactualizado"?
# MAGIC Se usa el P25 de `days_since_end_location` del grupo inactivo como punto de corte conservador.

# COMMAND ----------

gps = spark.table("lakehouse.silver.gps_location").filter(F.col("business_date") == FECHA)
display(
    gps.filter(F.col("days_since_end_location") > 0)
    .select(F.percentile_approx("days_since_end_location", [0.25, 0.5, 0.75, 0.9]).alias("p25_p50_p75_p90"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Segmentación de recencia cruzada con riesgo y atraso

# COMMAND ----------

cartera = (
    spark.table("lakehouse.gold.portfolio_overview")
    .filter(F.col("business_date") == FECHA)
    .select("vin", "contract_number", "dpd", "bucket")
)
riesgo = spark.table("lakehouse.risk.contract_scores").groupBy("contract_number").agg(F.max_by("band", "week_date").alias("band"))

seg = (
    cartera.join(riesgo, "contract_number", "left")
    .join(gps.select("vin", "lat", "lon", "days_since_end_location"), "vin", "left")
    .withColumn("recencia",
        F.when(F.col("days_since_end_location").isNull(), "SIN GPS")
         .when(F.col("days_since_end_location") <= UMBRAL_DIAS, f"≤ {UMBRAL_DIAS} días")
         .otherwise(f"> {UMBRAL_DIAS} días"))
)
display(seg.groupBy("recencia", "band").agg(F.count("*").alias("contratos"), F.round(F.avg("dpd"), 1).alias("dpd_prom")).orderBy("recencia", "band"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. DBSCAN (haversine) sobre unidades en atraso con GPS vigente
# MAGIC `eps` en radianes = km / radio de la Tierra.

# COMMAND ----------

pdf = (
    seg.filter((F.col("bucket") >= 4) & (F.col("recencia") == f"≤ {UMBRAL_DIAS} días"))
    .select("vin", "lat", "lon").toPandas()
)
coords = np.radians(pdf[["lat", "lon"]].to_numpy(dtype=float))
db = DBSCAN(eps=1.0 / 6371.0, min_samples=5, metric="haversine", algorithm="ball_tree").fit(coords)
pdf["cluster"] = db.labels_
print(pdf["cluster"].value_counts().head(10))
