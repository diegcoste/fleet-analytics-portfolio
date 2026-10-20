# 10 · BI Design System para Tableau

> Kit para que cualquier analista construya un dashboard con el mismo estándar visual y de calidad, sin inventar estilos: tema, paletas, shapes, plantilla base y checklist de publicación.

## Contenido del kit

| Pieza | Qué es |
|---|---|
| `Preferences.tps` | Paletas categórica, secuencial y divergente (claro/oscuro) que aparecen en el selector de Tableau |
| `theme.json` | Tema de libro de trabajo: tipografía y colores base |
| Shapes | Íconos de estado (▲ ▼ ✓ ✗, puntos de semáforo) como paleta de formas |
| `dashboard-base.twbx` | Plantilla con la estructura de contenedores y cálculos estándar (Δ vs LY, etc.) |
| Guía de estilo | Cada regla con su valor exacto — ver [`guia-de-estilo.md`](guia-de-estilo.md) |
| Checklist de publicación | 19 puntos sí/no antes de publicar — ver [`checklist-publicacion.md`](checklist-publicacion.md) |

## Layout estándar

```
┌──────────┬──────────────────────────────────────┐
│ SIDEBAR  │  KPI BAND (5 posiciones, 110 px)     │
│ 240 px   ├──────────────────────────────────────┤
│          │  CUERPO fila 1 (flexible)            │
│ · logo   ├──────────────────────────────────────┤
│ · usuario│  CUERPO fila 2 (flexible)            │
│ · periodo├──────────────────────────────────────┤
│ · filtros│  FOOTER 28 px                        │
└──────────┴──────────────────────────────────────┘
          Tamaño fijo 1400 × 850
```

## Reglas de oro

- Paleta categórica asignada **en orden** con "Asignar paleta"; nunca colores a mano.
- Semáforo solo para **estado** y siempre con ícono (▲▼✓✗).
- Un solo eje: nunca eje dual con dos escalas.
- Títulos con patrón **"Métrica por dimensión · periodo"**.
- Filtros solo en el sidebar; separación por espacio, no por bordes ni sombras.
- Contenedores nombrados (`c-sidebar`, `c-kpis`, `c-footer`, …).
