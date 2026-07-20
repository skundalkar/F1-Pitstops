"""Provider boundaries for future, opt-in public-data integrations.

These adapters intentionally do not make HTTP calls yet.  Each provider has
different availability and licensing terms, so activation belongs in an
explicit ingestion command, never in Streamlit page rendering.
"""

from __future__ import annotations

from .contracts import RaceWeekend, WeekendSource


class SourceNotConfigured(RuntimeError):
    """Raised when a live/public source has not been enabled for this install."""


class _StubSource(WeekendSource):
    provider_name = "unknown"
    source_url = ""
    coverage_note = ""

    def fetch_weekend(self, season: int, round_number: int) -> RaceWeekend:
        raise SourceNotConfigured(
            f"{self.provider_name} is not configured. Use the bundled seed dataset "
            "or run a future explicit ingestion command."
        )


class FastF1Source(_StubSource):
    """Future historical session adapter for laps, stints, timing and telemetry."""

    provider_name = "FastF1"
    source_url = "https://docs.fastf1.dev/"
    coverage_note = "Historical session data; coverage and field quality vary by session."


class OpenF1Source(_StubSource):
    """Future current-session adapter for laps, stints, pits and race control."""

    provider_name = "OpenF1"
    source_url = "https://openf1.org/docs/"
    coverage_note = "Public current/recent session API; not official timing."


class OpenMeteoSource(_StubSource):
    """Future forecast/historical-weather adapter, normalized to probability 0..1."""

    provider_name = "Open-Meteo"
    source_url = "https://open-meteo.com/en/docs"
    coverage_note = "Forecast/historical weather; attribution and forecast timestamps required."
