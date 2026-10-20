# Databricks notebook source
# MAGIC %md
# MAGIC # Carga y normalización de reportes de aseguradoras
# MAGIC Unity Catalog no permite `spark.read.csv` sobre `/Workspace/...`, así que se lee con pandas y se convierte.

# COMMAND ----------

import pandas as pd
from pyspark.sql import functions as F

BASE = "/Workspace/Shared/siniestros/brokers"
FUENTES = {
    "ASEGURADORA_A": f"{BASE}/aseguradora_a.csv",
    "ASEGURADORA_B": f"{BASE}/aseguradora_b.csv",
}

# Columnas homologadas que deben existir en ambos reportes
COLS = ["SERIE", "SINIESTRO", "FECSINIESTRO", "ESTATUS", "TIPO", "SUBESTATUS"]

# COMMAND ----------

def normalizar(pdf: pd.DataFrame, broker: str) -> pd.DataFrame:
    pdf = pdf.rename(columns=lambda c: str(c).strip().upper())
    faltantes = set(COLS) - set(pdf.columns)
    if faltantes:
        raise ValueError(f"{broker}: faltan columnas {faltantes}")
    pdf = pdf[COLS].astype("string")
    # Quitar TODO el whitespace y pasar a mayúsculas (los reportes traen espacios intermedios)
    for c in COLS:
        pdf[c] = pdf[c].str.replace(r"\s+", "", regex=True).str.upper()
    pdf["BROKER"] = broker
    return pdf

frames = [normalizar(pd.read_csv(path, dtype=str, encoding="latin-1"), broker)
          for broker, path in FUENTES.items()]

sdf = (
    spark.createDataFrame(pd.concat(frames, ignore_index=True))
    .withColumn("FECSINIESTRO", F.try_to_date(F.trim("FECSINIESTRO"), "d/M/yyyy"))
)
sdf.createOrReplaceTempView("excel_broker_sinister_raw")

display(sdf.groupBy("BROKER", "ESTATUS").count().orderBy("BROKER", "ESTATUS"))
