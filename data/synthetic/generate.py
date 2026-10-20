"""Genera datos 100 % sintéticos para correr la demo sin acceso a ninguna fuente real.

    python data/synthetic/generate.py [--unidades 500] [--seed 42]

Salida en data/synthetic/out/: unidades.csv, entregas.csv, readmisiones.csv, multas.csv
"""
from __future__ import annotations

import argparse
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

OUT = Path(__file__).parent / "out"
CIUDADES = ["ciudad_a", "ciudad_b", "ciudad_c", "ciudad_d", "ciudad_e"]
MARCAS = {"Marca1": ["M1-Sedan", "M1-Hatch"], "Marca2": ["M2-SUV"], "Marca3": ["M3-EV", "M3-Sedan"]}


def rand_date(rng: random.Random, a: date, b: date) -> date:
    return a + timedelta(days=rng.randint(0, (b - a).days))


def main(n: int, seed: int) -> None:
    rng = random.Random(seed)
    hoy = date(2026, 10, 8)
    unidades, entregas, readm, multas = [], [], [], []

    for i in range(1, n + 1):
        uid = f"U{i:05d}"
        marca = rng.choice(list(MARCAS))
        rec = rand_date(rng, date(2023, 1, 1), date(2026, 3, 1))
        unidades.append({"unit_id": uid, "vehicle_state": rng.choice(CIUDADES), "brand": marca,
                         "model": rng.choice(MARCAS[marca]), "reception_date": rec})

        # 0 a 3 ciclos entrega → (readmisión)
        cursor = rec + timedelta(days=rng.randint(5, 40))
        for ciclo in range(rng.choice([0, 1, 1, 2, 2, 3])):
            if cursor >= hoy:
                break
            entregas.append({"unit_id": uid, "delivery_date": cursor})
            dur = rng.randint(30, 400)
            fin = cursor + timedelta(days=dur)
            if fin < hoy and rng.random() < 0.6:
                readm.append({"unit_id": uid, "readmission_date": fin})
                cursor = fin + timedelta(days=rng.randint(7, 60))
            else:
                break

        for _ in range(rng.choice([0, 0, 1, 2, 3, 5])):
            f = rand_date(rng, rec - timedelta(days=30), hoy)  # algunas caen antes de recepción a propósito
            multas.append({"unit_id": uid, "folio": f"F{rng.randint(10**6, 10**7)}", "violation_date": f,
                           "amount": round(rng.choice([350, 520, 870, 1200, 2600]) * rng.uniform(0.9, 1.1), 2),
                           "status": rng.choice(["paid", "unpaid", "unpaid", "unknown"])})

    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in [("unidades", unidades), ("entregas", entregas), ("readmisiones", readm), ("multas", multas)]:
        pd.DataFrame(rows).to_csv(OUT / f"{name}.csv", index=False)
    print(f"✔ {len(unidades)} unidades · {len(entregas)} entregas · {len(readm)} readmisiones · {len(multas)} multas → {OUT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--unidades", type=int, default=500)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    main(a.unidades, a.seed)
