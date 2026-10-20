"""Reglas de calendario usadas en los reportes."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta


def lunes_de(d: date) -> date:
    """Lunes de la semana (lunes–domingo) que contiene a `d`."""
    return d - timedelta(days=d.weekday())


def week_to_month(d: date) -> str:
    """Mes ('YYYY-MM') al que pertenece la semana de `d`: el mes en que cae su jueves.

    Evita que una semana partida entre dos meses se cuente en ambos.
    Equivale a la regla ISO-8601 para asignar semanas a años.
    """
    jueves = lunes_de(d) + timedelta(days=3)
    return f"{jueves.year:04d}-{jueves.month:02d}"


def dias_habiles(inicio: date, fin: date, feriados: Iterable[date] = ()) -> int:
    """Días hábiles en (inicio, fin]: lunes a viernes, excluyendo feriados.

    Mismo criterio que la vista `tramites_con_habiles`: el día de la solicitud no cuenta,
    el día de cierre sí.
    """
    if fin <= inicio:
        return 0
    fer = set(feriados)
    n = 0
    d = inicio + timedelta(days=1)
    while d <= fin:
        if d.weekday() < 5 and d not in fer:
            n += 1
        d += timedelta(days=1)
    return n
