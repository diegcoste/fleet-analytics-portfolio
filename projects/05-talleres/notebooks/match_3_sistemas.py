# Databricks notebook source
# MAGIC %md
# MAGIC # D3 · Match de 3 sistemas (app · proveedor · ticketera)
# MAGIC Un VIN con trabajo de taller abierto debería existir en los tres sistemas a la vez (cliente activo)
# MAGIC o al menos en app y proveedor (unidad de stock). Este notebook mide cuántos lo cumplen y genera
# MAGIC la **cola diaria de conciliación** (Plan B).

# COMMAND ----------

from pyspark.sql import functions as F

def norm_vin(c):
    return F.regexp_replace(F.upper(F.trim(F.col(c))), r"\s+", "")

# App: unidades en estatus Taller
app = (
    spark.table("lakehouse.silver.fleet_stock_vehicles")
    .filter((F.col("country") == "Mexico") & (F.col("category") == "workshop"))
    .select(norm_vin("vin").alias("vin"),
            (F.col("last_driver_id").isNotNull() & (F.col("status") == "active")).alias("cliente_activo"))
    .dropDuplicates(["vin"])
    .withColumn("en_app", F.lit(True))
)

# Proveedor: órdenes correctivas abiertas
prov = (
    spark.table("lakehouse.silver.workshop_vendor_orders")
    .filter((F.col("order_type") == "corrective") & F.col("completion_date").isNull())
    .select(norm_vin("vin").alias("vin")).distinct()
    .withColumn("en_proveedor", F.lit(True))
)

# Ticketera: tickets abiertos de categoría taller/mantenimiento
tkt = (
    spark.table("lakehouse.silver.tickets")
    .filter(F.col("category_name").isin("Taller", "Mantenimiento") & (F.col("status") != "closed"))
    .select(norm_vin("vin").alias("vin")).distinct()
    .withColumn("en_ticketera", F.lit(True))
)

# COMMAND ----------

universo = (
    app.join(prov, "vin", "full").join(tkt, "vin", "full")
    .fillna(False, subset=["en_app", "en_proveedor", "en_ticketera", "cliente_activo"])
    .withColumn("n_sistemas", F.col("en_app").cast("int") + F.col("en_proveedor").cast("int") + F.col("en_ticketera").cast("int"))
    .withColumn(
        "cumple_regla",
        F.when(F.col("cliente_activo"), F.col("en_app") & F.col("en_proveedor") & F.col("en_ticketera"))
         .otherwise(F.col("en_app") & F.col("en_proveedor"))
    )
    .withColumn(
        "combinacion",
        F.concat_ws(" + ",
            F.when(F.col("en_app"), F.lit("App")),
            F.when(F.col("en_proveedor"), F.lit("Proveedor")),
            F.when(F.col("en_ticketera"), F.lit("Ticketera")))
    )
    .cache()
)
universo.createOrReplaceTempView("df_final_match_vins")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumen

# COMMAND ----------

total = universo.count()
display(
    universo.groupBy("combinacion", "n_sistemas")
    .agg(F.count("*").alias("vins"))
    .withColumn("pct", F.round(F.col("vins") / F.lit(total) * 100, 2))
    .orderBy(F.desc("n_sistemas"), F.desc("vins"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Plan B · Cola diaria de conciliación

# COMMAND ----------

cola = (
    universo.filter(~F.col("cumple_regla"))
    .withColumn(
        "accion",
        F.when(~F.col("en_app"), "Actualizar estatus en app a Taller o cerrar orden/ticket huérfano")
         .when(~F.col("en_proveedor"), "Abrir orden con el proveedor o sacar la unidad de estatus Taller")
         .when(F.col("cliente_activo") & ~F.col("en_ticketera"), "Abrir ticket para el cliente activo")
    )
    .withColumn("prioridad", F.when(F.col("cliente_activo"), "P1").otherwise("P2"))
    .select("vin", "prioridad", "cliente_activo", "combinacion", "accion")
    .orderBy("prioridad", "combinacion")
)
display(cola)
