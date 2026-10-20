from datetime import date

import pytest

from fleetlib.responsibility import (
    ANTES_RECEPCION,
    CLIENTE_ACTUAL,
    CLIENTE_ANTERIOR,
    SIN_CLIENTE,
    clasificar,
)

REC = date(2025, 1, 10)
ENT = [date(2025, 2, 1), date(2025, 8, 1)]
REA = [date(2025, 6, 15)]


@pytest.mark.parametrize(
    "multa, esperado",
    [
        (date(2025, 1, 5), ANTES_RECEPCION),    # antes de que la unidad fuera nuestra
        (date(2025, 1, 20), SIN_CLIENTE),       # recibida pero aún no entregada
        (date(2025, 2, 1), CLIENTE_ANTERIOR),   # el día de la entrega ya es del cliente
        (date(2025, 3, 1), CLIENTE_ANTERIOR),   # cliente 1, que después regresó la unidad
        (date(2025, 6, 15), SIN_CLIENTE),       # el día de la readmisión ya no es del cliente
        (date(2025, 7, 1), SIN_CLIENTE),        # entre readmisión y nueva entrega
        (date(2025, 9, 1), CLIENTE_ACTUAL),     # cliente 2, sin readmisión posterior
    ],
)
def test_linea_de_tiempo_completa(multa, esperado):
    assert clasificar(multa, REC, ENT, REA) == esperado


def test_unidad_nunca_entregada():
    assert clasificar(date(2025, 5, 1), REC, [], []) == SIN_CLIENTE


def test_readmision_sin_nueva_entrega_queda_sin_cliente():
    assert clasificar(date(2025, 12, 1), REC, [date(2025, 2, 1)], [date(2025, 6, 1)]) == SIN_CLIENTE


def test_sin_reception_date_no_rompe():
    assert clasificar(date(2025, 3, 1), None, [date(2025, 2, 1)], []) == CLIENTE_ACTUAL


def test_entregas_duplicadas_se_ignoran():
    assert clasificar(date(2025, 3, 1), REC, [date(2025, 2, 1)] * 3, []) == CLIENTE_ACTUAL
