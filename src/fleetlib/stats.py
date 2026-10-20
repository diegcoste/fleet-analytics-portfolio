"""Estadísticos robustos usados en los análisis."""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from statistics import median


def percentile(values: Sequence[float], q: float) -> float:
    """Percentil con interpolación lineal (equivalente a `percentile()` de Spark SQL)."""
    if not values:
        raise ValueError("lista vacía")
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def iqr_bounds(values: Sequence[float], k: float = 1.5) -> tuple[float, float]:
    q1, q3 = percentile(values, 0.25), percentile(values, 0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def median_iqr(values: Iterable[float], k: float = 1.5) -> float:
    """Mediana excluyendo outliers fuera de [Q1 − k·IQR, Q3 + k·IQR]."""
    xs = [v for v in values if v is not None]
    lo, hi = iqr_bounds(xs, k)
    return median([v for v in xs if lo <= v <= hi])
