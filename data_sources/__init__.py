"""Small, explicit adapters for public Formula 1 data.

The application starts from the bundled seed dataset.  Live adapters remain
opt-in so opening the app never implies a background download.
"""

from .contracts import RaceWeekend, TyreCompound, WeatherSnapshot
from .seed import load_seed_weekend

__all__ = ["RaceWeekend", "TyreCompound", "WeatherSnapshot", "load_seed_weekend"]
