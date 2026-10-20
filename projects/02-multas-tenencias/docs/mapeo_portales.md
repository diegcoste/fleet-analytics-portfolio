# 🗺️ Mapeo de portales de consulta (multas y tenencias)

Para automatizar la obtención de multas y tenencias primero se mapeó, por cada ciudad de la flotilla, **qué entidad de gobierno emite el dato y cómo se consulta**. La terminología: `vehicle_state` = ciudad de la flotilla en la app; **entidad** = gobierno emisor.

## Esquema del mapeo

| Columna | Descripción |
|---|---|
| `vehicle_state` | Ciudad de la flotilla |
| `entidad` | Gobierno emisor (estado o municipio) |
| `has_api` | ¿Existe API o convenio de datos? |
| `link_n_type` | `violations` · `tenancy` · `all` |
| `link_n_requirements` | `plate`, `vin`, `motor_number`, `razon social`, `username/password` |
| `link_n_has_captcha` / `captcha_type` | `recaptcha` · `cloudflare` · `letters` |
| `link_n_is_business` | ¿Portal empresarial (consulta por flotilla)? |

> Las credenciales de portales empresariales **no** viven en el mapeo: se guardan en un *secret scope* y el extractor las lee en tiempo de ejecución.

## Resumen por tipo de acceso (genérico)

| Patrón | Qué implica para automatizar |
|---|---|
| Consulta por placa sin captcha | Automatizable directo (requests / Playwright) |
| Consulta por placa con captcha de letras | OCR o servicio de resolución; costo por consulta |
| Consulta con reCAPTCHA / Cloudflare Turnstile | Barrera anti-bot: priorizar convenio o portal empresarial |
| Portal empresarial por flotilla | Mejor opción: una sesión, toda la flota, sin captcha |
| API / convenio de datos | Ideal: sin extracción, dato oficial y trazable |

## Estrategia

1. **Portales empresariales primero** (ya gestionados en varias entidades).
2. **Convenios de colaboración** con las entidades de mayor flotilla para recibir datos por API.
3. **Scraping** solo donde no exista lo anterior, con un **proceso de excepciones**: las consultas fallidas se re-corren con reglas y solo el residual pasa a captura manual.
4. Todo aterriza en una **tabla homologada** (ver [`../scraping/`](../scraping)).
