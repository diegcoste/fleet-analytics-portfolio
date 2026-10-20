# Paginación en Tableau con visibilidad de zona dinámica

**Problema:** el área central del dashboard necesita mostrar varias gráficas sin comprimirlas, manteniendo fijos los KPIs, el sidebar y el footer. Los contenedores nativos no permiten scroll independiente de varias hojas.

**Solución:** un dashboard con "páginas" controladas por parámetro.

## 1. Parámetro

| Propiedad | Valor |
|---|---|
| Nombre | `p_Pagina` |
| Tipo | Entero |
| Valor actual | 1 |
| Valores permitidos | Lista: `1 · Resumen`, `2 · Pendientes`, `3 · Ubicación` |

## 2. Campos calculados booleanos

```tableau
// Ver_Resumen
[p_Pagina] = 1

// Ver_Pendientes
[p_Pagina] = 2

// Ver_Ubicacion
[p_Pagina] = 3
```

Agregar cada uno a **Marcas → Detalle** de una hoja de su página para que estén disponibles como opción de visibilidad.

## 3. Estructura de contenedores (modo Mosaico)

```text
c-main
├── c-kpis                         [siempre visible]
└── c-paginas                      [vertical]
    ├── pagina-resumen             [vertical]   → Ver_Resumen
    │   ├── FLUJO_periodo
    │   └── ANTIGUEDAD_legal
    ├── pagina-pendientes          [vertical]   → Ver_Pendientes
    │   └── COLAS_pendientes
    └── pagina-ubicacion           [horizontal] → Ver_Ubicacion
        ├── MAPA_gps        (~70 %)
        └── SINGPS_ciudad   (~30 %)
```

En **Trazado → Jerarquía de elementos**, seleccionar cada contenedor de página → *Controlar la visibilidad usando el valor* → asignar su campo.

## 4. Selector

Mostrar `p_Pagina` como lista de valor único dentro de `c-sidebar`, **fuera** de cualquier contenedor condicional para que siempre sea accesible.

## 5. Filtros flotantes por página

1. Un contenedor vertical flotante por página con sus filtros **dentro** (verificar la relación padre/hijo en la jerarquía, no basta con superponerlos).
2. Asignar la misma visibilidad que su página. Los tres pueden compartir X/Y y tamaño.

> ⚠️ **Ocultar un filtro no lo desactiva.** Sigue afectando las hojas configuradas. Para filtros exclusivos de una página: menú del filtro → *Aplicar a hojas de trabajo → Hojas seleccionadas* → solo las de esa página.

## Checklist de validación

- [ ] Solo una página y un grupo de filtros visibles a la vez.
- [ ] KPIs, sidebar, footer y selector siempre visibles.
- [ ] Dimensiones fijas se mantienen al alternar páginas.
- [ ] El alcance de cada filtro coincide con la intención.

Referencia: documentación oficial de Tableau sobre *dynamic zone visibility*.
