# Databricks notebook source
# MAGIC %md
# MAGIC # Fix global de `Decimal` en `toPandas()` + plantilla de gráfica KPI
# MAGIC Spark devuelve `ROUND()`, `AVG()` y `PERCENTILE()` como `decimal.Decimal`; Matplotlib no puede operar con ellos.
# MAGIC Este patch convierte cualquier columna `Decimal` a `float64` en todos los `toPandas()` del notebook.

# COMMAND ----------

import decimal

import matplotlib.pyplot as plt
import pandas as pd
from pyspark.sql import DataFrame as SparkDF

_original_to_pandas = SparkDF.toPandas

def _to_pandas_float(self, *args, **kwargs) -> pd.DataFrame:
    pdf = _original_to_pandas(self, *args, **kwargs)
    for c in pdf.columns:
        if pdf[c].dtype == object and pdf[c].map(lambda x: isinstance(x, decimal.Decimal)).any():
            pdf[c] = pdf[c].astype("float64")
    return pdf

SparkDF.toPandas = _to_pandas_float

# COMMAND ----------

def grafica_kpi(pdf: pd.DataFrame, x: str, y: str, meta: float, titulo: str, fmt: str = "{:.0f}%"):
    """Línea del KPI con meta punteada y etiqueta directa en el último punto."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(pdf[x], pdf[y], lw=2, color="#4F46E5")
    ax.axhline(meta, ls="--", lw=1, color="#6B7280")
    ax.text(pdf[x].iloc[0], meta, f" meta {fmt.format(meta)}", va="bottom", color="#6B7280", fontsize=9)
    ax.annotate(fmt.format(pdf[y].iloc[-1]), (pdf[x].iloc[-1], pdf[y].iloc[-1]),
                xytext=(6, 0), textcoords="offset points", va="center", fontsize=10, weight="bold")
    ax.set_title(titulo, loc="left", fontsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E5E7EB")
    plt.tight_layout()
    return fig

# Uso:
# pdf = spark.sql("SELECT mes, tasa_completitud FROM ...").toPandas()
# grafica_kpi(pdf, "mes", "tasa_completitud", meta=85, titulo="Tasa de completitud por mes")
