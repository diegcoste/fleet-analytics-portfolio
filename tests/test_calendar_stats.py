from datetime import date

import pytest

from fleetlib.calendar import dias_habiles, lunes_de, week_to_month
from fleetlib.stats import iqr_bounds, median_iqr, percentile


@pytest.mark.parametrize(
    "d, mes",
    [
        (date(2026, 9, 28), "2026-10"),  # lunes; su jueves es 1-oct
        (date(2026, 9, 30), "2026-10"),  # miércoles de la misma semana
        (date(2026, 10, 4), "2026-10"),  # domingo de la misma semana
        (date(2026, 8, 31), "2026-09"),  # lunes 31-ago; jueves 3-sep
        (date(2026, 12, 31), "2026-12"), # jueves mismo
        (date(2027, 1, 1), "2026-12"),   # viernes 1-ene pertenece a la semana del jueves 31-dic
    ],
)
def test_week_to_month(d, mes):
    assert week_to_month(d) == mes


def test_lunes_de():
    assert lunes_de(date(2026, 10, 4)) == date(2026, 9, 28)


def test_dias_habiles_excluye_fin_de_semana_y_feriados():
    # vie 2-oct-2026 → vie 9-oct-2026: lun..vie = 5 hábiles
    assert dias_habiles(date(2026, 10, 2), date(2026, 10, 9)) == 5
    assert dias_habiles(date(2026, 10, 2), date(2026, 10, 9), feriados=[date(2026, 10, 5)]) == 4
    assert dias_habiles(date(2026, 10, 9), date(2026, 10, 2)) == 0


def test_percentile_lineal():
    assert percentile([1, 2, 3, 4], 0.5) == 2.5
    assert percentile([10], 0.9) == 10


def test_median_iqr_excluye_outliers():
    vals = [3, 4, 5, 5, 6, 7, 8, 9, 120, 300]
    _, hi = iqr_bounds(vals)
    assert hi < 120
    assert median_iqr(vals) == 5.5
