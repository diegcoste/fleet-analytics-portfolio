# PRD (resumen) — App de Siniestros / Checklist

## Objetivo

Reemplazar el seguimiento de siniestros en hojas de cálculo por una app con flujo definido, alertas y datos estructurados que alimenten directamente el lakehouse.

## Módulos

| Módulo | Contenido |
|---|---|
| **Ciclo de vida de póliza** | Alta, endosos, renovación, cancelación, vinculación por VIN |
| **Siniestro end-to-end** | Reporte → ajuste → valuación → reparación o pérdida total → cierre → recuperación del deducible |
| **Subprocesos financieros** | Deducibles, pagos a taller, indemnizaciones, salvamentos, conciliación con aseguradora |
| **Checklist** | Pasos obligatorios por tipo de siniestro con evidencia |
| **Alertas** | Especificación por `category` / `sub_category` (se preservan exactamente esos nombres de campo para no romper integraciones) |

## Alertas (ejemplos)

| category | sub_category | Disparador |
|---|---|---|
| ubicacion | cerrado_en_taller | Siniestro cerrado y la unidad sigue en geocerca de taller > N días |
| ubicacion | perdida_total_sin_gps | Pérdida total sin posición GPS reciente |
| tiempo | reparacion_excedida | Valuación/reparación abierta > SLA del tipo de daño |
| conciliacion | solo_en_aseguradora | El reporte de la aseguradora trae un siniestro que la app no tiene |

## Entregables de diseño

Diagramas de flujo por tipo de siniestro (una lámina por tipo), estructura de datos, y reglas de transición de estatus.
