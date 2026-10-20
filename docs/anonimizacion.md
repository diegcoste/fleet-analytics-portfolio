# 🔒 Política de anonimización

Este repositorio es un portafolio público. Todo lo que aparece aquí pasó por estas reglas antes de publicarse.

## Qué se reemplazó

| Original | En el repo |
|---|---|
| Nombre de la empresa y marca | "la empresa", "la flota" |
| Catálogos y esquemas reales | `lakehouse.bronze` / `lakehouse.silver` / `lakehouse.gold` |
| Nombres de tablas internas | Nombres genéricos y descriptivos (`fleet_stock_vehicles`, `portfolio_overview`, …) |
| Proveedores (gestoría, taller, aseguradoras, compradores) | `proveedor_gestoria`, `proveedor_taller`, `Aseguradora A` / `Aseguradora B`, `Comprador X` |
| Personas (colegas, clientes, conductores) | Eliminadas |
| Rutas de usuario (`/Workspace/Users/...`) | `/Workspace/Shared/<proyecto>/` |
| Cifras de negocio (montos, conteos, % de cumplimiento) | Eliminadas o expresadas como rangos cualitativos |

## Qué nunca se publica

- Datos reales: VIN, placas, contratos, montos individuales, ubicaciones GPS, IDs de conductor.
- Credenciales, API keys, usuarios/contraseñas de portales, RFC o datos fiscales.
- Exportes (`.csv`, `.xlsx`, `.twbx`, `.pbix`) generados desde producción.
- Logos, paletas propietarias o material de marca.

## Qué sí se conserva

- La **lógica**: queries, transformaciones, reglas de negocio, algoritmos.
- La **estructura** de los notebooks y dashboards.
- Información **pública**: tipos de portales de gobierno para consultar multas/tenencias, legislación (LFT art. 74), documentación oficial de herramientas.

## Cómo se verificó

Antes de cada push se ejecuta un escaneo de cadenas sensibles (nombres internos, dominios de correo, patrones de VIN de 17 caracteres, placas, llaves tipo `api_key=`). Ver [`scripts/scan_sensitive.py`](../scripts/scan_sensitive.py).
