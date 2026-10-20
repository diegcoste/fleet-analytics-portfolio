"""Demo rápida: `python -m fleetlib.demo`"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from statistics import mean, median

from .calendar import week_to_month
from .responsibility import clasificar
from .stats import median_iqr

SYNTH = Path(__file__).resolve().parents[2] / "data" / "synthetic" / "out"


def _demo_sintetico() -> None:
    import pandas as pd

    unidades = pd.read_csv(SYNTH / "unidades.csv", parse_dates=["reception_date"])
    entregas = pd.read_csv(SYNTH / "entregas.csv", parse_dates=["delivery_date"])
    readm = pd.read_csv(SYNTH / "readmisiones.csv", parse_dates=["readmission_date"])
    multas = pd.read_csv(SYNTH / "multas.csv", parse_dates=["violation_date"])

    ent = entregas.groupby("unit_id")["delivery_date"].apply(lambda s: [d.date() for d in s]).to_dict()
    rea = readm.groupby("unit_id")["readmission_date"].apply(lambda s: [d.date() for d in s]).to_dict()
    rec = unidades.set_index("unit_id")["reception_date"].dt.date.to_dict()

    multas["responsable"] = [
        clasificar(r.violation_date.date(), rec.get(r.unit_id), ent.get(r.unit_id, []), rea.get(r.unit_id, []))
        for r in multas.itertuples()
    ]
    print("\n▶ Monto de multas por responsable (datos sintéticos)")
    print(multas.groupby("responsable")["amount"].agg(["count", "sum"]).round(0).sort_values("sum", ascending=False))


def main() -> None:
    print("▶ Regla semana → mes (jueves)")
    for d in [date(2026, 9, 28), date(2026, 9, 30), date(2026, 10, 2), date(2026, 12, 31)]:
        print(f"   {d.isoformat()} ({d.strftime('%a')}) → {week_to_month(d)}")

    print("\n▶ Mediana IQR")
    dias = [3, 4, 5, 5, 6, 7, 8, 9, 120, 300]
    print(f"   valores={dias}\n   media={mean(dias):.1f}  mediana={median(dias)}  mediana IQR={median_iqr(dias)}")

    print("\n▶ Atribución de una multa")
    caso = {"reception_date": date(2025, 1, 10),
            "entregas": [date(2025, 2, 1), date(2025, 8, 1)],
            "readmisiones": [date(2025, 6, 15)]}
    for f in [date(2025, 1, 5), date(2025, 1, 20), date(2025, 3, 1), date(2025, 7, 1), date(2025, 9, 1)]:
        print(f"   multa {f} → {clasificar(f, **caso)}")

    if (SYNTH / "multas.csv").exists():
        _demo_sintetico()
    else:
        print("\n(Corre `python data/synthetic/generate.py` para ver la demo con datos sintéticos.)")


if __name__ == "__main__":
    main()
