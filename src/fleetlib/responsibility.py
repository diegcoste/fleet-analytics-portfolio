"""Atribución temporal de multas a responsable.

Implementación en Python puro de la misma lógica del notebook PySpark
(`projects/02-multas-tenencias/notebooks/clasificacion_responsable.py`), para poder testearla.

Línea de tiempo de una unidad:

    reception ──► entrega_1 ──► readmisión_1 ──► entrega_2 ──► …

Reglas, en orden:
    1. multa < reception_date                          → antes_recepcion
    2. multa ∈ [entrega_n, readmisión_n)               → cliente_anterior
       multa ∈ [entrega_n, ∞) sin readmisión posterior → cliente_actual
    3. multa ∈ [readmisión_n, siguiente entrega)       → sin_cliente
    4. sin entregas, o multa < primera entrega          → sin_cliente
    5. otro caso                                        → timeline_inconsistente
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

ANTES_RECEPCION = "antes_recepcion"
CLIENTE_ACTUAL = "cliente_actual"
CLIENTE_ANTERIOR = "cliente_anterior"
SIN_CLIENTE = "sin_cliente"
INCONSISTENTE = "timeline_inconsistente"


@dataclass(frozen=True)
class Periodo:
    inicio: date
    fin: date | None  # None = abierto
    responsable: str

    def contiene(self, d: date) -> bool:
        return d >= self.inicio and (self.fin is None or d < self.fin)


def construir_periodos(entregas: Iterable[date], readmisiones: Iterable[date]) -> list[Periodo]:
    """Reconstruye todas las ventanas de cliente y sin cliente de una unidad."""
    ent = sorted(set(entregas))
    rea = sorted(set(readmisiones))
    periodos: list[Periodo] = []

    # Ventanas de cliente: cada entrega la abre; la cierra la primera readmisión antes de la siguiente entrega
    for i, e in enumerate(ent):
        siguiente = ent[i + 1] if i + 1 < len(ent) else None
        cierre = next((r for r in rea if r >= e and (siguiente is None or r < siguiente)), None)
        periodos.append(Periodo(e, cierre, CLIENTE_ACTUAL if cierre is None else CLIENTE_ANTERIOR))

    # Ventanas sin cliente: de cada readmisión a la siguiente entrega posterior
    for r in rea:
        siguiente = next((e for e in ent if e > r), None)
        periodos.append(Periodo(r, siguiente, SIN_CLIENTE))

    return periodos


def clasificar(
    fecha_multa: date,
    reception_date: date | None,
    entregas: Iterable[date],
    readmisiones: Iterable[date],
) -> str:
    """Devuelve el responsable de una multa."""
    entregas = list(entregas)
    if reception_date is not None and fecha_multa < reception_date:
        return ANTES_RECEPCION

    periodos = construir_periodos(entregas, readmisiones)
    # La ventana de cliente tiene prioridad sobre la de sin cliente (igual que en el notebook)
    for p in sorted(periodos, key=lambda p: p.responsable == SIN_CLIENTE):
        if p.contiene(fecha_multa):
            return p.responsable

    if not entregas or fecha_multa < min(entregas):
        return SIN_CLIENTE
    return INCONSISTENTE
