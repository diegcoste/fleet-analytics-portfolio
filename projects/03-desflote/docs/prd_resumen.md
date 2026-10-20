# PRD (resumen) — Migración del proceso de desflote a la plataforma de ventas

## Problema

El proceso de desflote vivía en un Google Sheet con captura manual: inventario, ofertas de compradores, asignaciones, facturación y cobranza. Consecuencias: sin trazabilidad de cambios, reglas de negocio implícitas en fórmulas, y un dashboard que dependía de que nadie moviera una columna.

## Objetivo

Migrar el proceso a la plataforma de ventas como sistema de registro, con **Databricks como fuente única** y un dashboard en **Tableau**.

## Alcance (bloques de requerimientos)

| Bloque | Ejemplos de requerimientos |
|---|---|
| Inventario | Estatus único por unidad, motivo de no disponibilidad, condición, costo de reparación |
| Ofertas | Captura por comprador, estados (pendiente / autorizada / rechazada), auditoría de cambios |
| Asignación | Fecha de asignación como inicio del SLA, reasignaciones registradas |
| Facturación y cobro | Fechas de factura y pago, monto, cartera por cobrar |
| Reglas | Valor por condición, prioridad de precio, regla semana→mes |
| Reporting | Funnel, forecast vs real, SLA por mes de asignación, ticket promedio vs OLV |
| No funcionales | Refresh diario, permisos por rol, histórico sin sobrescritura |

En total ~56 requerimientos funcionales, cada uno con criterio de aceptación.

## Entregables del paquete

PRD · brief ejecutivo · presentación C-level · documento de clasificación de variables (fuente, tipo, regla, dueño) · workbook de mapeo Sheet → plataforma · diagrama de flujo · `CONTEXT.md` para que cualquier persona (o asistente de IA) retome el proyecto sin contexto previo.
