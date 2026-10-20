# 🔎 Metodología: de dato a decisión

Todos los análisis de este portafolio siguen la misma estructura. El objetivo es que un director pueda leer solo los títulos y saber qué pasa y qué se va a hacer.

## 1. Antes de escribir una query

| Paso | Salida |
|---|---|
| Discovery con el área | Audiencia, decisión que habilita, preguntas que debe contestar |
| Inventario de fuentes | Qué campos existen, su granularidad y — sobre todo — **qué no existe** |
| Reglas de negocio por escrito | Universo, tratamiento de nulos, casos frontera. Firmadas por el área |
| Fecha de corte | Fija y visible en el encabezado del notebook |

## 2. Formato de cada hallazgo

```
## Discovery N — <afirmación en una frase, con el número clave>

**Hallazgo.**     Qué pasa, con datos y su fuente.
**Conclusión.**   Por qué pasa (causa raíz) y qué impacto tiene.
**Plan A — resolución de raíz.**    Cambios de proceso / sistema / gobierno.
**Plan B — contener y operar.**     Qué hacemos mañana mientras el Plan A se implementa.
```

## 3. Elegir el estadístico correcto (no mostrar todos los percentiles)

Un error común es presentar media, mediana, P75, P90 y P95 de todo. Se elige **un** estadístico por métrica según la forma de la distribución y la pregunta:

| Situación | Estadístico | Por qué |
|---|---|---|
| Aging con un pico de ingresos reciente que "rejuvenece" el promedio | **Mediana** | La media queda sesgada hacia abajo |
| Tiempo entre cambios de estatus (mayoría rápida, cola de casos abandonados) | **P90** | La mediana oculta los tickets olvidados |
| Primer comentario cuando hay respuestas automáticas | **P90** | La mediana ≈ 0 refleja al bot, no a la persona |
| Tiempo de resolución con outliers lentos | **Mediana** | La media se infla con pocos casos |
| Diseño de un SLA nuevo | **P90 del histórico maduro** | Ancla la meta en lo que la operación sí logra |
| Valores con outliers por segmento | **Mediana IQR** | Se excluye lo que cae fuera de `[Q1−1.5·IQR, Q3+1.5·IQR]` |

## 4. Metas justificadas por datos

Ninguna meta es un número redondo inventado. Cada KPI trae:

1. **Query de derivación** (ej. P75 de las tasas mensuales de meses maduros).
2. **Query principal** que mide el KPI.
3. **Gráfica**.

Y se evita la **lógica circular**: no se deriva una meta del mismo periodo que se está evaluando.

## 5. "Sin dato" no es "cero"

Un estado con flotilla grande y **0 multas** es un hueco de información, no flotilla limpia. Cada análisis separa explícitamente:

- ✅ **Tenemos** — dato completo y confiable.
- ⚠️ **Parcial** — existe pero con huecos, estatus `unknown`, o cobertura incompleta.
- ❌ **No tenemos** — el campo no existe; se documenta para pedirlo.
