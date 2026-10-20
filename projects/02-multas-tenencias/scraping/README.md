# 🤖 PoC — Extracción automatizada de infracciones

Prueba de concepto validada localmente: consulta por placa en un portal estatal, parseo del HTML y salida a una **tabla homologada** lista para cargar al lakehouse.

## Stack

Python · Playwright (navegación) · BeautifulSoup (parseo) · pandas (estructura) · zona horaria `America/Mexico_City`.

## Esquema homologado

| Campo | Tipo | Descripción |
|---|---|---|
| `plate` | string | Placa consultada |
| `entity` | string | Entidad emisora |
| `folio` | string | Identificador de la infracción en la secretaría |
| `violation_date` | timestamp (ISO 8601 con zona) | Fecha y hora de la infracción |
| `amount` | double | Monto a pagar |
| `status` | string | `PENDIENTE` / `PAGADA` |
| `concept` | string | Motivo de la infracción (si el portal lo trae) |
| `payment_date` | date | Fecha de pago (si aplica) |
| `source_url` | string | Portal consultado |
| `extracted_at` | timestamp | Momento de extracción |

## Estado y siguientes pasos

- ✅ Consulta, extracción y parseo por placa funcionando en local.
- ⏳ Superar la barrera anti-bot (Cloudflare Turnstile) → se prioriza portal empresarial / convenio.
- ⏳ Integrar como job desatendido en Databricks con credenciales en *secret scope*.
- ⏳ Reglas de re-intento y cola de excepciones.

## Uso

```bash
pip install playwright beautifulsoup4 pandas
playwright install chromium
export PORTAL_URL="https://<portal-de-consulta>"
python extractor_poc.py --plates plates.txt --out infracciones.csv
```

> Respeta los términos de uso de cada portal y la frecuencia de consulta. La ruta preferida siempre es un convenio de datos con la entidad.
