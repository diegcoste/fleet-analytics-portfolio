# Trabajo complementario del portafolio

Esta página incorpora trabajo profesional reciente que complementa las diez líneas de proyecto principales. Los casos se agrupan por problema de negocio para evitar duplicar el catálogo. No se publican archivos operativos, datos de personas, VIN, ubicaciones precisas, nombres de proveedores ni métricas internas.

## 1. Dashboard operativo de Legal

**Problema:** ayudar al equipo operativo a ver el backlog y encontrar cuellos de botella en los trámites.

**Aporte:** diseño de un tablero de seguimiento con filtros para la cartera legal, avance por etapa, antigüedad frente al promedio, unidades readmitidas, cobertura GPS/geocerca y colas priorizadas. Se cuidó que los indicadores usaran nombres consistentes y que el flujo mostrara el estado operativo de forma clara.

**Complementa:** [Legal Tracker](../projects/07-legal-tracker) y [Geoespacial & GPS](../projects/08-geoespacial).

## 2. Medición de tiempos y desempeño de talleres y gestoría

**Problema:** comparar tiempos de atención y desempeño entre trámites, ciudades y operación de talleres.

**Aporte:** definición de métricas de tiempo y SLA, análisis por ciudad y proceso, y consultas SQL para relacionar citas de taller con información de GPS y del vehículo. Se trabajó la selección de la cita relevante por unidad y la parametrización de fechas objetivo.

**Complementa:** [Talleres — Discoveries](../projects/05-talleres) y [Gestoría — KPIs](../projects/06-gestoria-kpis).

## 3. Líneas de tiempo por etapa y categoría

**Problema:** entender cómo avanza cada caso entre etapas y categorías, y dónde se acumulan demoras.

**Aporte:** análisis de secuencias STEP/CATEGORY y subcategorías para ordenar eventos en el tiempo, construir indicadores de avance y hacer visibles los cambios de estado.

**Complementa:** [Multas & Tenencias](../projects/02-multas-tenencias), [Talleres — Discoveries](../projects/05-talleres) y [Legal Tracker](../projects/07-legal-tracker).

## 4. Análisis geoespacial y mapas de concentración

**Problema:** visualizar dónde se concentran unidades y hacer utilizable la ubicación GPS en herramientas de BI.

**Aporte:** extracción de latitud y longitud desde geometrías, preparación de campos para mapas de calor y guía para llevarlos a Google Sheets o Looker Studio. La ubicación exacta se mantiene fuera de este repositorio.

**Complementa:** [Geoespacial & GPS](../projects/08-geoespacial).

## 5. Indicador de días para vender

**Problema:** explicar cuánto tardan en venderse las unidades durante un periodo.

**Aporte:** definición breve del KPI mensual: días promedio hasta la venta de las unidades vendidas en el mes, con título y subtítulo pensados para lectura rápida en un dashboard.

**Complementa:** [Desflote (venta de unidades)](../projects/03-desflote).

## 6. Navegación de dashboards y preparación de datos

**Problema:** conservar legibilidad en dashboards con muchas vistas y dejar conjuntos tabulares listos para análisis geográfico.

**Aporte:** diseño documentado para dividir un dashboard de Tableau en páginas con visibilidad dinámica de vistas y filtros; además, consolidación de hojas de datos tabulares en una salida homogénea, preservando códigos con ceros iniciales.

**Estado:** el trabajo de Tableau quedó como guía de implementación; no se modificó directamente el libro de Tableau. Los archivos fuente y los datos consolidados no se incluyen aquí.

**Complementa:** [BI Design System](../projects/10-bi-design-system) y [Geoespacial & GPS](../projects/08-geoespacial).

## Criterio de publicación

Los casos describen el problema y el enfoque de trabajo. Para hacerlos reproducibles, se deben añadir únicamente ejemplos nuevos con datos sintéticos y código revisado para anonimización. Los archivos de clientes, exports operativos, capturas con datos reales y enlaces a dashboards internos no forman parte del portafolio.
