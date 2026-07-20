"""Load the deterministic, offline demo weekend shipped with the repository."""

from __future__ import annotations

import json
from pathlib import Path

from .contracts import DriverGridEntry, RaceWeekend, TyreCompound, WeatherSnapshot

SEED_WEEKEND_PATH = Path(__file__).parent / "fixtures" / "sample_race_weekend.json"


def load_seed_weekend(path: Path = SEED_WEEKEND_PATH) -> RaceWeekend:
    """Return a repeatable demo weekend without network or provider credentials."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    drivers = tuple(
        DriverGridEntry(
            driver=row["driver"],
            team=row["team"],
            grid_position=row["grid_position"],
            available_compounds=tuple(TyreCompound(item) for item in row["available_compounds"]),
        )
        for row in payload["drivers"]
    )
    weather_data = payload["weather"]
    return RaceWeekend(
        season=payload["season"],
        round_number=payload["round_number"],
        event_name=payload["event_name"],
        circuit_name=payload["circuit_name"],
        laps=payload["laps"],
        pit_lane_loss_seconds=payload["pit_lane_loss_seconds"],
        drivers=drivers,
        weather=WeatherSnapshot(**weather_data),
        data_mode="offline_seed",
    )
