# 📗 Fórmulas clave (Google Sheets)

Fórmulas de producción del workbook de desflote, con nombres de hojas genéricos. Todas leen de `AUXILIARES` o de las hojas fuente; ninguna escribe sobre ellas.

---

## 1. Precio con prioridad y fallback (`SUMPRODUCT`)

Toma el precio de la oferta autorizada; si no hay, la oferta pendiente; si no hay, el OLV del inventario.

```gs
=LET(
  vin, A2,
  aut, SUMPRODUCT((OFERTAS!$A$2:$A=vin) * (OFERTAS!$E$2:$E="authorized") * OFERTAS!$D$2:$D),
  pen, SUMPRODUCT((OFERTAS!$A$2:$A=vin) * (OFERTAS!$E$2:$E="pending")    * OFERTAS!$D$2:$D),
  olv, SUMPRODUCT((INVENTARIO!$A$2:$A=vin) * INVENTARIO!$K$2:$K),
  IFS(aut>0, aut, pen>0, pen, TRUE, olv)
)
```

## 2. Clasificación de condición con `LET` + `LAMBDA`

```gs
=MAP(AUXILIARES!F2:F, AUXILIARES!G2:G,
  LAMBDA(costo, olv,
    IF(olv="", "",
      LET(r, costo / olv,
        IFS(r <= 0.10, "Buena", r <= 0.30, "Media", TRUE, "Mala")))))
```

## 3. Vista de detalle dinámica (`FILTER` + `CHOOSECOLS`)

Un selector de mes en `B1` devuelve solo las columnas que el usuario necesita, en el orden que las necesita.

```gs
=IFERROR(
  CHOOSECOLS(
    FILTER(DBX_DATA!A2:Z, DBX_DATA!Z2:Z = $B$1, DBX_DATA!T2:T <> ""),
    1, 3, 4, 20, 17, 18, 22),
  "Sin ventas en el mes")
```

## 4. Semana → mes por jueves

```gs
=LET(f, A2, jueves, f - WEEKDAY(f, 2) + 4, TEXT(jueves, "yyyy-mm"))
```

`WEEKDAY(f, 2)` → lunes = 1 … domingo = 7. Restar el día de la semana y sumar 4 lleva siempre al jueves de esa semana.

## 5. Proyección con promedio móvil por marca × ciudad

```gs
=LET(
  marca, $A2, ciudad, $B2, mes, C$1,
  meses, SEQUENCE(3, 1, 1, 1),
  ventas, MAP(meses, LAMBDA(k,
            COUNTIFS(AUXILIARES!$C:$C, marca, AUXILIARES!$D:$D, ciudad,
                     AUXILIARES!$Z:$Z, TEXT(EDATE(mes, -k), "yyyy-mm")))),
  ROUND(AVERAGE(ventas), 0)
)
```

## 6. Lookup vectorizado con `XLOOKUP` + `MAP`

```gs
=MAP(A2:A, LAMBDA(vin, IF(vin="", "", XLOOKUP(vin, DBX_DATA!A:A, DBX_DATA!T:T, "—"))))
```

---

### Lecciones aprendidas

- `SWITCH` no devuelve arreglos → usar `IFS` o un `FILTER` con condiciones multiplicadas.
- Celdas combinadas bloquean la expansión de `FILTER` → descombinar el rango de salida.
- `IFERROR` durante el diagnóstico esconde el error real → agregarlo solo al final.
- En `QUERY`, columnas tipo fecha se filtran con `is not null`, no con `<> 'null'`.
