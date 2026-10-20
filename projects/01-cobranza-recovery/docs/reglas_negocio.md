# Reglas de negocio — Cobranza & Recovery

Documento que se entregó a las áreas junto con cada lista. Cualquier número de las vistas se puede reproducir con estas reglas.

## 1. Bands de riesgo

| Elemento | Condición | Resultado | Nota |
|---|---|---|---|
| NUEVO (Onboard) | ≤ 28 días desde `contract_start_date` | `band = NUEVO` | Prioridad sobre el score |
| A (Protect) | > 28 días y band = A | `band = A` | Menor riesgo |
| B (Manage) | > 28 días y band = B | `band = B` | Riesgo medio-bajo |
| C (Test) | > 28 días y band = C | `band = C` | Riesgo medio-alto |
| D (Recover) | > 28 días y band = D | `band = D` | Mayor riesgo |
| Sin band | > 28 días y sin score | Excluido | No aparece en la lista |
| Score usado | Semana más reciente (`max(week_date)`) | `score`, `band` | Solo la última calificación |

## 2. Acción a tomar (Cobranza)

El día de pago es el lunes. `dpd_calc` = días respecto al último lunes de pago.

| Band | `dpd_calc` | Acción |
|---|---|---|
| NUEVO | −4 a −1 | Seguimiento (faltan 1–4 días para pagar) |
| NUEVO | 0 | Seguimiento (día de pago) |
| NUEVO | 1 a 4 | Cobranza |
| NUEVO | ≥ 7 | Regularización / Recovery |
| A | 0 | Seguimiento |
| A | 1 a 2 | Cobranza |
| B–D | ≥ 1 | Cobranza, con prioridad creciente por band |

## 3. Segmentación Strategic Recovery

| Segmento | Bucket | Objetivo |
|---|---|---|
| RETENER | 1–2 | Que el cliente se ponga al corriente y conserve la unidad |
| REACTIVAR | 3 | Reactivar pagos |
| REDEFINIR R / R | 4–10 | Reestructura o recuperación de la unidad |
| LEGAL | ≥ 11 | Gestión legal |
| Sin segmento | 0 o vacío | Casos con `dpd` alto pero bucket 0 se reportan aparte como inconsistencia |

## 4. Región de recuperación

Cada `vehicle_state` (código de ciudad de la flotilla) se asigna a una de cuatro regiones operativas de campo. La tabla de mapeo vive en un `CASE` dentro de la vista base para que cualquier ciudad nueva quede explícitamente sin región (y salte en el control de calidad) en lugar de asignarse por defecto.
