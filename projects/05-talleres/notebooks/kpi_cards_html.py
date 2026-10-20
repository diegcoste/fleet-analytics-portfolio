# Databricks notebook source
# MAGIC %md
# MAGIC # Celda autocontenida: KPI cards + donut con `displayHTML`
# MAGIC Cada celda de visualización trae su propia paleta, datos e imports para que corra en cualquier orden.

# COMMAND ----------

import plotly.graph_objects as go

PALETA = {"primario": "#4F46E5", "ok": "#0F9D58", "alerta": "#F59E0B", "mal": "#DC2626", "tinta": "#111827", "suave": "#6B7280"}

# Datos de ejemplo (sintéticos)
kpis = [
    ("VINs con trabajo abierto", "1,000", PALETA["primario"]),
    ("Match en 3 sistemas", "3 %", PALETA["mal"]),
    ("Viven en un solo sistema", "80 %", PALETA["alerta"]),
]
combinaciones = {"Solo App": 420, "Solo Proveedor": 260, "Solo Ticketera": 120, "App + Proveedor": 150, "App + Ticketera": 20, "Los 3": 30}

cards = "".join(
    f"""<div style="flex:1;background:#fff;border-top:3px solid {c};border-radius:8px;padding:14px 16px;
             box-shadow:0 1px 2px rgba(0,0,0,.06)">
          <div style="font:600 10px system-ui;letter-spacing:.08em;color:{PALETA['suave']};text-transform:uppercase">{t}</div>
          <div style="font:700 28px system-ui;color:{PALETA['tinta']};margin-top:6px">{v}</div>
        </div>"""
    for t, v, c in kpis
)

fig = go.Figure(go.Pie(labels=list(combinaciones), values=list(combinaciones.values()), hole=0.6, sort=False))
fig.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10), showlegend=True, font=dict(family="system-ui"))

displayHTML(f"""
<div style="display:flex;gap:12px;font-family:system-ui;margin-bottom:12px">{cards}</div>
{fig.to_html(full_html=False, include_plotlyjs='cdn')}
""")
