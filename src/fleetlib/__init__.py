"""fleetlib — lógica de negocio reutilizable del portafolio, en Python puro y testeada."""
from .calendar import dias_habiles, week_to_month
from .responsibility import clasificar
from .stats import median_iqr

__all__ = ["clasificar", "dias_habiles", "median_iqr", "week_to_month"]
__version__ = "1.0.0"
