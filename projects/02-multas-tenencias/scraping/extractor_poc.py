"""PoC: extracción de infracciones por placa hacia un esquema homologado.

Las URLs, selectores y credenciales se leen de variables de entorno: nada sensible vive en el código.

    PORTAL_URL       URL del formulario de consulta por placa
    PORTAL_INPUT     selector CSS del input de placa       (default: input[name='placa'])
    PORTAL_SUBMIT    selector CSS del botón de búsqueda    (default: button[type='submit'])
    PORTAL_ROWS      selector CSS de las filas de resultado (default: table tbody tr)
"""
from __future__ import annotations

import argparse
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from bs4 import BeautifulSoup

TZ = ZoneInfo("America/Mexico_City")


@dataclass
class Infraccion:
    plate: str
    entity: str
    folio: str | None
    violation_date: str | None
    amount: float | None
    status: str | None
    concept: str | None
    payment_date: str | None
    source_url: str
    extracted_at: str


def parse_amount(text: str | None) -> float | None:
    if not text:
        return None
    clean = re.sub(r"[^0-9.\-]", "", text)
    return float(clean) if clean else None


def parse_datetime(text: str | None) -> str | None:
    """Convierte 'dd/mm/yyyy hh:mm[:ss]' a ISO 8601 con zona CDMX."""
    if not text:
        return None
    text = text.strip()
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=TZ).isoformat()
        except ValueError:
            continue
    return None


def parse_results(html: str, plate: str, entity: str, url: str, rows_selector: str) -> list[Infraccion]:
    """Parsea la tabla de resultados. Asume columnas: folio | fecha | concepto | monto | estatus."""
    soup = BeautifulSoup(html, "html.parser")
    now = datetime.now(TZ).isoformat()
    out: list[Infraccion] = []
    for tr in soup.select(rows_selector):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(cells) < 5:
            continue
        folio, fecha, concepto, monto, estatus = cells[:5]
        out.append(
            Infraccion(
                plate=plate,
                entity=entity,
                folio=folio or None,
                violation_date=parse_datetime(fecha),
                amount=parse_amount(monto),
                status=(estatus or "").upper() or None,
                concept=concepto or None,
                payment_date=None,
                source_url=url,
                extracted_at=now,
            )
        )
    return out


def consultar(plates: list[str], entity: str) -> pd.DataFrame:
    from playwright.sync_api import sync_playwright  # import diferido: los tests no lo necesitan

    url = os.environ["PORTAL_URL"]
    sel_input = os.getenv("PORTAL_INPUT", "input[name='placa']")
    sel_submit = os.getenv("PORTAL_SUBMIT", "button[type='submit']")
    sel_rows = os.getenv("PORTAL_ROWS", "table tbody tr")

    registros: list[Infraccion] = []
    errores: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for plate in plates:
            try:
                page.goto(url, timeout=30_000)
                page.fill(sel_input, plate)
                page.click(sel_submit)
                page.wait_for_load_state("networkidle", timeout=30_000)
                registros += parse_results(page.content(), plate, entity, url, sel_rows)
            except Exception as exc:  # cola de excepciones: se re-intenta después
                errores.append({"plate": plate, "error": type(exc).__name__})
        browser.close()

    if errores:
        pd.DataFrame(errores).to_csv("excepciones.csv", index=False)
    return pd.DataFrame([asdict(r) for r in registros])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plates", required=True, help="archivo con una placa por línea")
    ap.add_argument("--entity", default="estado_x")
    ap.add_argument("--out", default="infracciones.csv")
    args = ap.parse_args()

    plates = [l.strip() for l in open(args.plates, encoding="utf-8") if l.strip()]
    df = consultar(plates, args.entity)
    df.to_csv(args.out, index=False)
    print(f"{len(df)} infracciones de {len(plates)} placas → {args.out}")


if __name__ == "__main__":
    main()
