"""Stable, provider-neutral shapes used by the strategy engine.

Providers expose different field names and coverage.  Adapters must normalize
their responses into these models before the rest of the product sees them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol


class TyreCompound(StrEnum):
    SOFT = "soft"
    MEDIUM = "medium"
    HARD = "hard"
    INTERMEDIATE = "intermediate"
    WET = "wet"


@dataclass(frozen=True)
class WeatherSnapshot:
    air_temperature_c: float
    track_temperature_c: float | None
    rain_probability: float
    wind_speed_kph: float | None
    source: str

    def __post_init__(self) -> None:
        if not 0 <= self.rain_probability <= 1:
            raise ValueError("rain_probability must be between 0 and 1")


@dataclass(frozen=True)
class DriverGridEntry:
    driver: str
    team: str
    grid_position: int
    available_compounds: tuple[TyreCompound, ...]


@dataclass(frozen=True)
class RaceWeekend:
    season: int
    round_number: int
    event_name: str
    circuit_name: str
    laps: int
    pit_lane_loss_seconds: float
    drivers: tuple[DriverGridEntry, ...]
    weather: WeatherSnapshot
    data_mode: str


@dataclass(frozen=True)
class DataProvenance:
    """Where a displayed brief came from, so it cannot be mistaken for live data."""

    provider: str
    dataset: str
    source_url: str | None
    retrieved_at: datetime
    is_live: bool


@dataclass(frozen=True)
class DataFreshness:
    """Human-readable freshness state intended for direct UI display."""

    label: str
    detail: str
    as_of: datetime


@dataclass(frozen=True)
class RaceBrief:
    """The complete typed payload an app page needs for a race briefing."""

    weekend: RaceWeekend
    provenance: DataProvenance
    freshness: DataFreshness


class WeekendSource(Protocol):
    """A provider adapter. Implementations must make network access explicit."""

    provider_name: str

    def fetch_weekend(self, season: int, round_number: int) -> RaceWeekend:
        """Return normalized weekend data or raise a descriptive provider error."""
