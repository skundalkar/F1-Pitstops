"""Load the deterministic, offline demo weekend shipped with the repository."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import DriverGridEntry, RaceWeekend, TyreCompound, WeatherSnapshot

SEED_WEEKEND_PATH = Path(__file__).parent / "fixtures" / "sample_race_weekend.json"


class SeedFixtureError(ValueError):
    """The local demo fixture is incomplete or has a value of the wrong shape."""


def _field(payload: dict[str, Any], name: str, context: str = "seed fixture") -> Any:
    try:
        return payload[name]
    except KeyError as error:
        raise SeedFixtureError(f"Missing required field '{name}' in {context}") from error


def load_seed_weekend(path: Path = SEED_WEEKEND_PATH) -> RaceWeekend:
    """Return a repeatable demo weekend without network or provider credentials."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SeedFixtureError("Seed fixture root must be a JSON object")
        driver_rows = _field(payload, "drivers")
        if not isinstance(driver_rows, list) or not driver_rows:
            raise SeedFixtureError("Field 'drivers' must be a non-empty list")
        drivers = tuple(
            DriverGridEntry(
                driver=_field(row, "driver", f"driver #{index}"),
                team=_field(row, "team", f"driver #{index}"),
                grid_position=_field(row, "grid_position", f"driver #{index}"),
                available_compounds=tuple(
                    TyreCompound(item)
                    for item in _field(row, "available_compounds", f"driver #{index}")
                ),
            )
            for index, row in enumerate(driver_rows, start=1)
        )
        weather_data = _field(payload, "weather")
        if not isinstance(weather_data, dict):
            raise SeedFixtureError("Field 'weather' must be an object")
        return RaceWeekend(
            season=_field(payload, "season"),
            round_number=_field(payload, "round_number"),
            event_name=_field(payload, "event_name"),
            circuit_name=_field(payload, "circuit_name"),
            laps=_field(payload, "laps"),
            pit_lane_loss_seconds=_field(payload, "pit_lane_loss_seconds"),
            drivers=drivers,
            weather=WeatherSnapshot(**weather_data),
            data_mode="offline_seed",
        )
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        if isinstance(error, SeedFixtureError):
            raise
        raise SeedFixtureError(f"Invalid seed fixture '{path.name}': {error}") from error
