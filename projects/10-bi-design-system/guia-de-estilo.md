# Guía de estilo — dashboards de Tableau

Cada regla tiene un valor exacto. Si algo dice "grande" o "bonito", es un bug de esta guía.

## 1. Tipografía

| Elemento | Peso | Tamaño | Color |
|---|---|---|---|
| Título del dashboard | SemiBold | 20 pt | `#111111` |
| Subtítulo / contexto | Regular | 11 pt | `#4B5563` |
| Título de sección | Medium | 12 pt | `#111111` |
| BAN (número de KPI) | SemiBold | 28 pt | `#111111` |
| Etiqueta de KPI | Medium, MAYÚSCULAS | 10 pt | `#6B7280` |
| Delta ▲▼ | SemiBold | 12 pt | `#006300` / `#B91C1C` |
| Ejes | Regular | 9 pt | `#6B7280` |
| Footer | Regular | 8 pt | `#9CA3AF` |

Máximo 2 pesos por vista · sin cursivas · el texto nunca usa el color de la serie.

## 2. Formatos de número

| Tipo | Formato | Ejemplo |
|---|---|---|
| Moneda | `$#,##0` | $45,210 |
| Moneda en BAN | `$#,##0.0,,"M"` | $4.2M |
| Porcentaje | `0.0%` | 12.4% |
| Delta | `+0.0%;-0.0%` | +8.3% |
| Conteo | `#,##0` | 1,204 |

## 3. Títulos

- Patrón **Métrica por dimensión · periodo** → "Ingresos por región · MTD julio".
- Solo mayúscula inicial. Prohibido "Dashboard de…", "Análisis de…".
- Si la hoja tiene título, el eje no lo repite.

## 4. Tooltips

```
<Dimensión>
Ingresos: <valor formateado>
Δ vs LY: <delta con signo>
% del total: <pct>
```

Sin botones de comando · sin nombres técnicos de campo · máximo 5 líneas.

## 5. Gráficos

- Gridlines solo horizontales `#E5E7EB`; sin bordes ni sombras.
- Barras ordenadas por valor (salvo orden natural); una sola serie = un solo color.
- Líneas de 2 px; máximo 4 series con etiqueta directa al final.
- **Un solo eje.** Dos escalas distintas = dos gráficos apilados.
- Pie/dona: máximo 3 segmentos y solo parte-de-todo.

## 6. Color

1. Paleta categórica en orden 1 → 8; 9+ series → "Otros" o small multiples.
2. Semáforo reservado para estado, siempre con ícono.
3. Magnitud → secuencial; desviación vs base → divergente. Nunca arcoíris para continuos.
4. Colores de bajo contraste sobre blanco exigen etiqueta directa.

## 7. Do / Don't

| ✅ Do | ❌ Don't |
|---|---|
| BAN con delta: `$4.2M ▲ +8.3% vs LY` | BAN solo, sin comparativo |
| Barras ordenadas, un color | Barras alfabéticas multicolor |
| Etiqueta directa al final de línea | Leyenda flotante |
| Dos gráficos apilados | Eje dual |
| Barras horizontales para 8 categorías | Pie de 8 rebanadas |
