# Checklist de publicación — Tableau Cloud

Cada punto es sí/no. Si algo es "más o menos", es no. Tiempo objetivo: < 10 minutos.

## A. Diseño y layout
- [ ] **1. Tamaño fijo** (1400 × 850 salvo excepción justificada).
- [ ] **2. Estructura estándar**: filtros solo en sidebar (fechas primero), KPI band arriba, footer con fuente + actualización + contacto.
- [ ] **3. Sin scroll interno** al 100 % de zoom.
- [ ] **4. Contenedores nombrados** (`c-*`); ningún "Horizontal (2)".
- [ ] **5. Separación por espacio**, sin bordes ni sombras.

## B. Color y tipografía
- [ ] **6. Paletas del kit** asignadas en orden; nunca colores manuales.
- [ ] **7. Regla de alivio**: colores de bajo contraste con etiqueta directa.
- [ ] **8. Semáforo solo para estado**, siempre con ícono.
- [ ] **9. Tipografía del kit** en todo el texto vivo.

## C. Contenido
- [ ] **10. Títulos con patrón**; ejes sin títulos redundantes.
- [ ] **11. Formatos de número estándar**.
- [ ] **12. KPIs con contexto** (delta vs LY/meta).
- [ ] **13. Tooltips limpios**.

## D. Datos y publicación
- [ ] **14. Conectado a Databricks (SSOT)**, no a un CSV local.
- [ ] **15. Extracto con refresh programado** y fecha dinámica en el footer.
- [ ] **16. Proyecto y permisos** verificados con un usuario de negocio real.
- [ ] **17. Prueba de vista limpia** en navegador/incógnito.

## E. Móvil (solo dashboards marcados 📱)
- [ ] **18. Layout de teléfono personalizado** (no el automático).
- [ ] **19. Probado en dispositivo real**.

**Excepciones:** se anotan en el PR con número y razón. Excepciones repetidas 2+ veces → cambia la regla o el template.
