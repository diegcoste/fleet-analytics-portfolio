# Databricks notebook source
# MAGIC %md
# MAGIC # D3b · Aging del desajuste y exposición de cashflow
# MAGIC Días que cada VIN lleva fuera de regla × tarifa diaria = exposición estimada.
# MAGIC La resolución de columnas es **defensiva**: si el nombre de la fecha cambia en la fuente, el notebook no truena.

# COMMAND ----------

from pyspark.sql import functions as F

FECHA_CORTE = "2026-06-01"
TARIFA_DIARIA = 500.0   # parámetro; reemplazar por la tarifa real por contrato cuando esté disponible

def pick(df, candidatos):
    """Devuelve la primera columna que exista en df, o None."""
    for c in candidatos:
        if c in df.columns:
            return c
    return None

ordenes = spark.table("lakehouse.silver.workshop_vendor_orders")
tickets = spark.table("lakehouse.silver.tickets")

c_ord = pick(ordenes, ["created_at", "createdAt", "order_date", "open_date"])
c_tkt = pick(tickets, ["created_at", "createdAt", "opened_at"])
assert c_ord and c_tkt, "No se encontró columna de fecha de apertura"

inicio = (
    ordenes.select(F.regexp_replace(F.upper("vin"), r"\s+", "").alias("vin"), F.to_date(c_ord).alias("f"))
    .unionByName(tickets.select(F.regexp_replace(F.upper("vin"), r"\s+", "").alias("vin"), F.to_date(c_tkt).alias("f")))
    .groupBy("vin").agg(F.min("f").alias("inicio_desajuste"))
)

# COMMAND ----------

exp = (
    spark.table("df_final_match_vins")
    .filter(~F.col("cumple_regla"))
    .join(inicio, "vin", "left")
    .withColumn("dias_desajuste", F.datediff(F.lit(FECHA_CORTE), "inicio_desajuste"))
    .withColumn("bucket", F.when(F.col("dias_desajuste") <= 30, "0-30")
                          .when(F.col("dias_desajuste") <= 90, "31-90")
                          .when(F.col("dias_desajuste") <= 180, "91-180")
                          .otherwise("180+"))
    .withColumn("exposicion", F.when(F.col("cliente_activo"), F.col("dias_desajuste") * F.lit(TARIFA_DIARIA)).otherwise(0.0))
)

display(
    exp.groupBy("bucket")
    .agg(F.count("*").alias("vins"),
         F.percentile_approx("dias_desajuste", 0.5).alias("mediana_dias"),
         F.round(F.sum("exposicion"), 0).alias("exposicion_estimada"))
    .orderBy("bucket")
)
