# Databricks notebook source
# MAGIC %md
# MAGIC # 🧩 Clasificación temporal de multas por responsable
# MAGIC
# MAGIC Reconstruye la **línea de tiempo** de cada unidad (recepción → entregas → readmisiones) y ubica cada multa
# MAGIC en la ventana correcta. A diferencia de la versión SQL simple (última entrega / última readmisión), aquí se
# MAGIC reconstruyen **todas** las ventanas de cliente, así que una unidad con 3 clientes se atribuye bien.
# MAGIC
# MAGIC | Orden | Regla | Responsable |
# MAGIC |---|---|---|
# MAGIC | 1 | Multa antes de `reception_date` | `antes_recepcion` |
# MAGIC | 2 | Dentro de `[entrega_n, readmisión_n)` con readmisión | `cliente_anterior` |
# MAGIC | 2 | Dentro de `[entrega_n, ∞)` sin readmisión posterior | `cliente_actual` |
# MAGIC | 3 | Dentro de `[readmisión_n, entrega_n+1)` | `sin_cliente` |
# MAGIC | 4 | Sin entregas, o antes de la primera entrega | `sin_cliente` |
# MAGIC | 5 | Ninguna de las anteriores | `timeline_inconsistente` (se reporta, no se esconde) |

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window

SRC_STOCK = "lakehouse.silver.fleet_stock_vehicles"
SRC_READM = "lakehouse.silver.fleet_readmissions"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Helpers de limpieza
# MAGIC `try_to_timestamp` devuelve `NULL` en lugar de romper el job cuando una fecha viene corrupta.

# COMMAND ----------

def parse_date_col(col_expr):
    s = col_expr.cast("string")
    return F.coalesce(
        F.try_to_timestamp(s, F.lit("yyyy-MM-dd")).cast("date"),
        F.try_to_timestamp(s, F.lit("yyyy-MM-dd'T'HH:mm:ss")).cast("date"),
        F.try_to_timestamp(s, F.lit("yyyy-MM-dd'T'HH:mm:ssXXX")).cast("date"),
        F.try_to_timestamp(s, F.lit("yyyy-MM-dd'T'HH:mm:ss.SSSXXX")).cast("date"),
        F.try_to_timestamp(s).cast("date"),
    )

def clean_upper(c):
    return F.upper(F.trim(F.col(c).cast("string")))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Bases limpias

# COMMAND ----------

df_stock = (
    spark.table(SRC_STOCK)
    .filter(F.col("country") == "Mexico")
    .select(
        F.col("stock_vehicles_id").cast("string").alias("stock_vehicle_id"),
        clean_upper("vin").alias("vin_norm"),
        F.lower(F.trim("vehicle_state")).alias("vehicle_state_norm"),
        parse_date_col(F.col("reception_date")).alias("reception_date"),
        F.transform("delivered_date", lambda x: parse_date_col(x)).alias("delivered_date_arr"),
        F.col("violations").alias("violations_arr"),
    )
    .cache()
)

df_readm = (
    spark.table(SRC_READM)
    .select(
        F.col("stock_vehicle_id").cast("string").alias("stock_vehicle_id"),
        parse_date_col(F.col("readmission_date")).alias("readmission_date"),
    )
    .filter(F.col("stock_vehicle_id").isNotNull() & F.col("readmission_date").isNotNull())
    .dropDuplicates()
    .cache()
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Entregas con secuencia y siguiente entrega

# COMMAND ----------

w_delivery = Window.partitionBy("stock_vehicle_id").orderBy("delivery_date")

df_deliveries = (
    df_stock
    .select("stock_vehicle_id", F.explode_outer("delivered_date_arr").alias("delivery_date"))
    .filter(F.col("delivery_date").isNotNull())
    .dropDuplicates(["stock_vehicle_id", "delivery_date"])
    .withColumn("delivery_seq", F.row_number().over(w_delivery))
    .withColumn("next_delivery_date", F.lead("delivery_date").over(w_delivery))
    .cache()
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Ventanas de cliente
# MAGIC Cada entrega abre una ventana. La cierra la **primera readmisión** entre esa entrega y la siguiente.
# MAGIC Si no hay readmisión, la ventana sigue abierta → es el cliente actual.

# COMMAND ----------

df_client_periods = (
    df_deliveries.alias("d")
    .join(
        df_readm.alias("r"),
        (F.col("d.stock_vehicle_id") == F.col("r.stock_vehicle_id"))
        & (F.col("r.readmission_date") >= F.col("d.delivery_date"))
        & (F.col("d.next_delivery_date").isNull() | (F.col("r.readmission_date") < F.col("d.next_delivery_date"))),
        "left",
    )
    .groupBy(F.col("d.stock_vehicle_id").alias("stock_vehicle_id"),
             F.col("d.delivery_seq").alias("delivery_seq"),
             F.col("d.delivery_date").alias("period_start"))
    .agg(F.min("r.readmission_date").alias("period_end"))
    .withColumn("responsable",
                F.when(F.col("period_end").isNull(), "cliente_actual").otherwise("cliente_anterior"))
    .cache()
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Ventanas sin cliente
# MAGIC De cada readmisión hasta la siguiente entrega (o abierta si la unidad no se ha vuelto a entregar).

# COMMAND ----------

df_no_client_periods = (
    df_readm.alias("r")
    .join(
        df_deliveries.select("stock_vehicle_id", "delivery_date").alias("d"),
        (F.col("r.stock_vehicle_id") == F.col("d.stock_vehicle_id"))
        & (F.col("d.delivery_date") > F.col("r.readmission_date")),
        "left",
    )
    .groupBy(F.col("r.stock_vehicle_id").alias("stock_vehicle_id"),
             F.col("r.readmission_date").alias("period_start"))
    .agg(F.min("d.delivery_date").alias("period_end"))
    .withColumn("responsable", F.lit("sin_cliente"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Multas (una fila por multa)

# COMMAND ----------

df_violations = (
    df_stock
    .select("stock_vehicle_id", "vin_norm", "vehicle_state_norm", "reception_date",
            F.posexplode_outer("violations_arr").alias("pos", "v"))
    .filter(F.col("v").isNotNull())
    .select(
        "stock_vehicle_id", "vin_norm", "vehicle_state_norm", "reception_date",
        (F.col("pos") + 1).alias("violation_seq"),
        F.trim(F.col("v.folio").cast("string")).alias("folio"),
        parse_date_col(F.col("v.violationDate")).alias("violation_date"),
        F.lower(F.trim(F.col("v.status").cast("string"))).alias("status_norm"),
        F.col("v.amount").cast("double").alias("amount"),
    )
    .withColumn("violation_key",
                F.concat_ws("||", "stock_vehicle_id", "violation_seq"))
    .cache()
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Join por rango y clasificación final

# COMMAND ----------

def hit(periods, label):
    return (
        df_violations.alias("v")
        .join(
            periods.alias("p"),
            (F.col("v.stock_vehicle_id") == F.col("p.stock_vehicle_id"))
            & (F.col("v.violation_date") >= F.col("p.period_start"))
            & (F.col("p.period_end").isNull() | (F.col("v.violation_date") < F.col("p.period_end"))),
            "inner",
        )
        .select("v.violation_key", F.col("p.responsable").alias(label))
        .dropDuplicates(["violation_key"])
    )

df_first_delivery = df_deliveries.groupBy("stock_vehicle_id").agg(F.min("delivery_date").alias("first_delivery_date"))

df_violations_classified = (
    df_violations
    .join(hit(df_client_periods, "client_period"), "violation_key", "left")
    .join(hit(df_no_client_periods, "no_client_period"), "violation_key", "left")
    .join(df_first_delivery, "stock_vehicle_id", "left")
    .withColumn(
        "responsable",
        F.when(F.col("reception_date").isNotNull() & (F.col("violation_date") < F.col("reception_date")), "antes_recepcion")
         .when(F.col("client_period").isNotNull(), F.col("client_period"))
         .when(F.col("no_client_period").isNotNull(), "sin_cliente")
         .when(F.col("first_delivery_date").isNull(), "sin_cliente")
         .when(F.col("violation_date") < F.col("first_delivery_date"), "sin_cliente")
         .otherwise("timeline_inconsistente")
    )
    .drop("client_period", "no_client_period")
    .cache()
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Resultado: monto por responsable (y control de inconsistencias)

# COMMAND ----------

w_total = Window.partitionBy()

display(
    df_violations_classified
    .groupBy("responsable")
    .agg(F.count("*").alias("multas"),
         F.countDistinct("stock_vehicle_id").alias("unidades"),
         F.round(F.sum("amount"), 2).alias("monto_total"),
         F.round(F.sum(F.when(F.col("status_norm") == "unpaid", F.col("amount")).otherwise(0)), 2).alias("monto_unpaid"))
    .withColumn("pct_monto", F.round(F.col("monto_total") / F.sum("monto_total").over(w_total) * 100, 2))
    .orderBy(F.desc("monto_total"))
)

# COMMAND ----------

# Un modelo temporal confiable debe tener ~0 filas aquí
display(df_violations_classified.filter(F.col("responsable") == "timeline_inconsistente"))
