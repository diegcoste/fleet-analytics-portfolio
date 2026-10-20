# 🧩 Patrones SQL reutilizables (Spark SQL / Databricks)

Recetario de soluciones que se repiten en los proyectos.

---

## 1. Mediana excluyendo outliers (IQR) por segmento

```sql
WITH bounds AS (
  SELECT segmento,
         percentile(valor, 0.25) AS q1,
         percentile(valor, 0.75) AS q3
  FROM base
  GROUP BY segmento
)
SELECT b.segmento,
       count(*) AS n,
       percentile(
         CASE WHEN x.valor BETWEEN b.q1 - 1.5 * (b.q3 - b.q1)
                               AND b.q3 + 1.5 * (b.q3 - b.q1)
              THEN x.valor END, 0.5)            AS mediana_iqr,
       sum(CASE WHEN x.valor > b.q3 + 1.5 * (b.q3 - b.q1) THEN 1 ELSE 0 END) AS outliers_altos
FROM base x
JOIN bounds b USING (segmento)
GROUP BY b.segmento
```

> `percentile` ignora `NULL`, así que el `CASE` sin `ELSE` filtra los outliers sin un subquery extra.

---

## 2. Deduplicación con prioridad de negocio

"Si hay un registro ABIERTO gana el abierto (y entre abiertos, el más antiguo); si no, el más reciente."

```sql
SELECT * EXCEPT (rn)
FROM (
  SELECT *,
         row_number() OVER (
           PARTITION BY vin
           ORDER BY
             CASE WHEN estatus = 'ABIERTO' THEN 0 ELSE 1 END,
             CASE WHEN estatus = 'ABIERTO' THEN fecha_siniestro END ASC,
             fecha_siniestro DESC
         ) AS rn
  FROM broker_union
)
WHERE rn = 1
```

---

## 3. Explode de `ARRAY<STRUCT>` conservando la unidad

```sql
SELECT u.*, m.folio, cast(m.violationDate AS DATE) AS violation_date, m.status, m.amount
FROM lakehouse.silver.fleet_stock_vehicles s
JOIN v_unidades u ON u.stock_vehicles_id = s.stock_vehicles_id
LATERAL VIEW explode(s.violations) t AS m
```

Para no perder unidades sin elementos: `LATERAL VIEW OUTER explode(...)`.

---

## 4. Último evento por entidad con `max_by`

```sql
SELECT stock_vehicle_id,
       max(readmission_date)                         AS ultima_readmission,
       max_by(readmission_reason, readmission_date)  AS motivo_ultima_readmission
FROM lakehouse.silver.fleet_readmissions
GROUP BY stock_vehicle_id
```

---

## 5. Flujo semanal: inicial, entradas, salidas, final

```sql
WITH semanal AS (
  SELECT contract_number,
         date_format(business_date, 'yyyy-ww') AS year_week,
         max_by(bucket, business_date)         AS bucket_cierre
  FROM base
  GROUP BY 1, 2
),
con_lag AS (
  SELECT *,
         lag(bucket_cierre) OVER (PARTITION BY contract_number ORDER BY year_week) AS bucket_prev
  FROM semanal
)
SELECT year_week,
       sum(CASE WHEN bucket_prev BETWEEN 2 AND 5 THEN 1 ELSE 0 END)                                  AS flujo_inicial,
       sum(CASE WHEN bucket_cierre BETWEEN 2 AND 5 AND NOT coalesce(bucket_prev BETWEEN 2 AND 5, false) THEN 1 ELSE 0 END) AS entradas,
       sum(CASE WHEN bucket_prev BETWEEN 2 AND 5 AND NOT coalesce(bucket_cierre BETWEEN 2 AND 5, false) THEN 1 ELSE 0 END) AS salidas,
       sum(CASE WHEN bucket_cierre BETWEEN 2 AND 5 THEN 1 ELSE 0 END)                                AS flujo_final
FROM con_lag
GROUP BY year_week
ORDER BY year_week
```

Identidad que debe cumplirse: `flujo_final = flujo_inicial + entradas − salidas`.

---

## 6. Comparación de dos snapshots (funnel)

```sql
WITH params AS (SELECT DATE '2026-09-01' AS f0, DATE '2026-09-29' AS f1),
a AS (SELECT contract_number, bucket FROM base, params WHERE business_date = f0),
b AS (SELECT contract_number, bucket FROM base, params WHERE business_date = f1)
SELECT
  count(DISTINCT CASE WHEN a.bucket BETWEEN 2 AND 10 THEN a.contract_number END)                         AS backlog_inicial,
  count(DISTINCT CASE WHEN a.contract_number IS NULL AND b.bucket BETWEEN 2 AND 10 THEN b.contract_number END) AS entradas,
  count(DISTINCT CASE WHEN a.bucket BETWEEN 2 AND 10 AND b.contract_number IS NULL THEN a.contract_number END) AS salidas,
  count(DISTINCT CASE WHEN a.bucket BETWEEN 2 AND 10 AND b.bucket BETWEEN 2 AND 10 THEN a.contract_number END) AS backlog_final,
  count(DISTINCT CASE WHEN a.bucket BETWEEN 2 AND 10 AND b.bucket >= 11 THEN a.contract_number END)          AS transiciono_a_legal
FROM a FULL OUTER JOIN b USING (contract_number)
```

---

## 7. Días hábiles con calendario (sin subqueries correlacionadas)

Se precalcula **una vez** y todas las queries de KPIs se unen contra la vista:

```sql
CREATE OR REPLACE TEMP VIEW tramites_con_habiles AS
SELECT t.*,
       (SELECT count(*) FROM lakehouse.dm.dim_calendario c
         WHERE c.es_habil AND c.fecha > t.fecha_solicitud AND c.fecha <= coalesce(t.fecha_cierre, DATE '2026-10-08')
       ) AS dias_habiles
FROM tramites t
```

> Versión más eficiente en [`projects/06-gestoria-kpis/sql/01_tramites_con_habiles.sql`](../projects/06-gestoria-kpis/sql/01_tramites_con_habiles.sql) usando un acumulado de días hábiles (`sum(es_habil) OVER (ORDER BY fecha)`) y dos joins de igualdad.

---

## 8. Varias métricas en una sola fila

```sql
SELECT
  (SELECT count(*)                FROM v_unidades) AS unidades,
  (SELECT count(*)                FROM v_multas)   AS multas,
  (SELECT round(sum(monto), 2)    FROM v_multas)   AS monto_total,
  (SELECT min(violation_date)     FROM v_multas)   AS primera_multa
```

---

## 9. División segura

```sql
round(try_divide(count(m.id), count(*)) * 100, 2) AS pct
-- PySpark: F.when(den == 0, None).otherwise(num / den)
```

---

## 10. Tabla de "qué tenemos / qué no" sin crear tablas

```sql
SELECT * FROM VALUES
  ('Folio',                 'folio',         '✅ Tenemos'),
  ('Fecha de infracción',   'violationDate', '✅ Tenemos'),
  ('Autoridad emisora',     '—',             '❌ No tenemos'),
  ('Fecha de pago',         '—',             '❌ No tenemos')
AS t(atributo, campo, estado)
```
