"""Small, explicit adapters for public Formula 1 data.

The application starts from the bundled seed dataset.  Live adapters remain
opt-in so opening the app never implies a background download.
"""

from .brief import load_offline_race_brief, map_offline_weekend_to_brief
from .contracts import DataFreshness, DataProvenance, RaceBrief, RaceWeekend, TyreCompound, WeatherSnapshot
from .seed import SeedFixtureError, load_seed_weekend

__all__ = [
    "DataFreshness",
    "DataProvenance",
    "RaceBrief",
    "RaceWeekend",
    "SeedFixtureError",
    "TyreCompound",
    "WeatherSnapshot",
    "load_offline_race_brief",
    "load_seed_weekend",
    "map_offline_weekend_to_brief",
]
