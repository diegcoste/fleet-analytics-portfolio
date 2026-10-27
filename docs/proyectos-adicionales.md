# Proyectos adicionales

Esta sección amplía los diez casos principales del portafolio con análisis, tableros y entregables trabajados en conversaciones posteriores. Los casos se relacionan con los proyectos existentes cuando comparten el mismo dominio, para que el portafolio conserve una sola historia por línea de negocio.

El nivel de detalle refleja lo que quedó documentado en el historial: cuando una tarea fue una definición o guía, se marca así; no se presenta como si se hubiera implementado en una herramienta.

> **Privacidad:** este repositorio no incluye bases operativas, VIN, coordenadas, archivos de clientes, nombres de proveedores ni cifras internas. Las descripciones son funcionales y anonimizadas.

## 1. Dashboard operativo de Legal

**Relacionado con:** [Legal Tracker](../projects/07-legal-tracker) · [Geoespacial & GPS](../projects/08-geoespacial)

### Contexto y objetivo

El equipo necesitaba una vista práctica para revisar su cartera legal, identificar casos detenidos y priorizar acciones. El foco fue presentar el estado operativo de las unidades y sus trámites en una sola experiencia de consulta.

### Diseño funcional

El tablero se organizó alrededor de preguntas de operación:

- ¿Cuántas unidades están dentro de la cartera legal y en qué etapa se encuentran?
- ¿Qué casos llevan más tiempo que el promedio histórico?
- ¿Qué unidades tienen cobertura GPS y cuáles aparecen dentro o fuera de geocerca?
- ¿Qué unidades fueron readmitidas y cómo avanzan en el flujo legal?
- ¿Qué casos conviene atender primero?

El diseño reunió filtros de cartera, avance por etapa, comparación de antigüedad contra el promedio, cobertura GPS/geocerca y una cola priorizada por unidad. También se normalizó el lenguaje de los indicadores para que cada tarjeta y sección describiera el mismo concepto con el mismo nombre.

### Resultado

Se iteró una versión operativa del dashboard con navegación y visualizaciones orientadas a detectar cuellos de botella. El portafolio describe su estructura sin publicar cortes, conteos ni datos que cambian con la operación.

### Habilidades demostradas

Diseño de métricas operativas · análisis de backlog · definición de filtros · visualización para priorización · comunicación de conceptos de negocio.

## 2. Métricas de desempeño para talleres y gestoría

**Relacionado con:** [Talleres — Discoveries](../projects/05-talleres) · [Gestoría — KPIs](../projects/06-gestoria-kpis)

### Contexto y objetivo

Se trabajó en medir tiempos y desempeño de procesos de taller y de trámites vehiculares. La necesidad era comparar resultados por tipo de trámite y ciudad, y construir métricas que permitieran distinguir retrasos del comportamiento normal.

### Enfoque analítico

- Se definieron indicadores de tiempo y cumplimiento para distintos procesos.
- Se consideraron cortes por trámite y ciudad, además de vistas agregadas para seguimiento.
- Se tomó como referencia la base existente de gestoría: cinco pilares y quince KPIs, con metas apoyadas en percentiles de periodos maduros y cálculo de días hábiles.
- Para el seguimiento de talleres, se preparó una consulta que relaciona citas con unidad y datos GPS. La lógica identifica la cita relevante por unidad y parametriza la fecha objetivo, incluyendo el ajuste de días no laborables del fin de semana.
- Se separó la preparación de datos de la presentación del indicador para que la regla de negocio pudiera revisarse antes de llevarla a un dashboard.

### Resultado

El trabajo amplía la medición de gestoría y talleres con consultas y definiciones más cercanas a la operación. No se publican nombres de tablas, proveedores, ciudades concretas ni resultados internos.

### Habilidades demostradas

SQL analítico · ventanas y deduplicación · calendarios de negocio · métricas de tiempo · segmentación geográfica · diseño de KPIs.

## 3. Líneas de tiempo por etapa, categoría y subcategoría

**Relacionado con:** [Multas & Tenencias](../projects/02-multas-tenencias) · [Talleres — Discoveries](../projects/05-talleres) · [Legal Tracker](../projects/07-legal-tracker)

### Pregunta de negocio

¿Cómo cambia un caso de etapa y categoría con el tiempo, y en qué parte del flujo se concentra la espera?

### Trabajo analítico

Se abordaron análisis de línea de tiempo para STEP/CATEGORY y para CATEGORY/SUBCATEGORY. El modelo de lectura consiste en ordenar los eventos por entidad y fecha, representar cada transición con su etapa y clasificación, y comparar la duración entre eventos. Esta vista permite explorar el recorrido completo, además de resumir el volumen por etapa o subcategoría.

Para convertirlo en una métrica operativa reproducible, cada implementación debe acordar el grano del caso, cómo resolver eventos con la misma fecha, qué hacer con cambios repetidos y cuál es la fecha de corte. Esas reglas evitan contar transiciones dos veces o atribuir demoras a la etapa incorrecta.

### Estado del caso

El historial disponible identifica el alcance de estas líneas de tiempo, pero no permite confirmar una regla final de transición ni un resultado cuantitativo único. Por eso se presenta como trabajo de análisis de procesos, sin afirmar cifras o impacto no documentados.

### Habilidades demostradas

Análisis de eventos · secuencias temporales · clasificación de procesos · definición de grano · preparación de métricas de duración.

## 4. GPS y mapas de concentración

**Relacionado con:** [Geoespacial & GPS](../projects/08-geoespacial)

### Contexto y objetivo

Se revisó cómo convertir una ubicación GPS almacenada como geometría a coordenadas que pudieran usarse en mapas y herramientas de BI.

### Preparación de datos

La recomendación fue exponer latitud y longitud como columnas separadas, conservar la unidad de análisis requerida por el mapa y excluir ubicaciones nulas. Para una geometría estándar, la latitud se obtiene con `ST_Y` y la longitud con `ST_X`. Esta forma es más práctica para exportar datos a una hoja o alimentar una visualización geográfica.

También se exploró el uso de un mapa de calor para distinguir zonas con diferentes concentraciones, manteniendo las coordenadas como ubicación y evitando reducirlas a una etiqueta de estado cuando se necesita granularidad espacial.

### Estado del caso

Esta conversación documentó la consulta de preparación y el enfoque para construir el mapa; no se confirmó la creación de un heatmap final en Sheets o Looker Studio. Los datos geográficos exactos no se incluyen. El modelado espacial más amplio, con H3 y agrupamiento, está descrito en el proyecto principal de Geoespacial & GPS.

### Habilidades demostradas

SQL espacial · geometrías · preparación de coordenadas · integración con BI · visualización de densidad.

## 5. KPI de días para vender

**Relacionado con:** [Desflote (venta de unidades)](../projects/03-desflote)

### Definición

Se afinó el nombre y la explicación de un indicador mensual para expresar cuántos días tardaron en venderse las unidades que se vendieron durante ese mes.

- **Título:** Días para vender
- **Subtítulo:** Promedio mensual de días hasta la venta.

La población del indicador son las unidades vendidas en el periodo; no representa el tiempo de venta de todo el inventario pendiente. Esa aclaración ayuda a interpretar correctamente la cifra y evita mezclar unidades vendidas con unidades aún disponibles.

### Aporte y estado

El trabajo se centró en la definición y comunicación del KPI para una tarjeta de dashboard. La lógica de negocio del funnel y del pronóstico de venta se encuentra en el proyecto principal de Desflote.

### Habilidades demostradas

Definición de KPI · selección de población · comunicación concisa · diseño de indicadores para dashboards.

## 6. Navegación por páginas en Tableau

**Relacionado con:** [BI Design System](../projects/10-bi-design-system) · [Legal Tracker](../projects/07-legal-tracker)

### Necesidad

Un dashboard tenía varias visualizaciones en el área central y requería conservar su tamaño legible, dejando fijos los indicadores principales y la navegación lateral.

### Diseño propuesto

La guía planteó separar la zona central en tres páginas de contenido:

1. **Resumen:** flujo del periodo y antigüedad de casos.
2. **Pendientes:** tabla de casos que necesita más espacio vertical.
3. **Ubicación:** mapa GPS y resumen por ciudad.

Un selector de página controla la visibilidad de cada contenedor. Los KPI, la barra lateral y el pie permanecen fijos; los filtros exclusivos de una página se agrupan con su contenido. También se documentó que ocultar un filtro no lo desactiva: cada filtro debe aplicarse solo a las hojas de trabajo correspondientes.

### Estado del caso

Se entregaron instrucciones paso a paso y una estructura sugerida para implementarlo en Tableau Desktop. El libro de Tableau no se abrió ni se modificó directamente, por lo que el comportamiento final debe validarse en el workbook.

### Habilidades demostradas

Diseño de dashboards · jerarquía de contenedores · visibilidad dinámica · navegación por parámetros · alcance de filtros.

## 7. Consolidación de hojas tabulares

**Relacionado con:** [Geoespacial & GPS](../projects/08-geoespacial) · [BI Design System](../projects/10-bi-design-system)

### Necesidad y tratamiento

Se consolidaron hojas de un archivo tabular en una salida única para facilitar su uso posterior. El tratamiento conservó una sola estructura de encabezados y protegió códigos que debían conservar ceros a la izquierda. Las hojas informativas se excluyeron del conjunto analítico.

### Resultado y privacidad

La consolidación se completó como una tarea de preparación de datos. El archivo original y el resultado contienen información operativa y no se suben al repositorio. Para mostrar este patrón de forma reproducible, se deberá construir una muestra sintética con el mismo tipo de transformación.

### Habilidades demostradas

Unificación de hojas · normalización de estructura · control de tipos · preservación de identificadores · preparación de datos para análisis.

## Cómo leer estos casos

Los diez proyectos principales contienen las líneas de trabajo con documentación técnica y ejemplos reproducibles. Esta página registra trabajos adicionales y extensiones recientes. Cada caso indica su nivel de implementación para distinguir entregables construidos, análisis documentados y guías que aún requieren validación en la herramienta original.
