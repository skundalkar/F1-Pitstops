"""Explicit source approval and immutable dataset provenance contracts.

No provider is implicitly approved merely because an adapter exists.  Ingestion
code must select an approved registry entry and emit a manifest alongside every
raw snapshot before curated data or features may be produced.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import re


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DATA_MODES = frozenset({"offline_seed", "historical_replay", "manual_live"})


@dataclass(frozen=True)
class SourceRegistryEntry:
    """A provider's reviewed use boundaries, not an adapter configuration."""

    provider: str
    source_url: str
    intended_use: str
    approved_for_ingestion: bool
    attribution_required: bool
    earliest_supported_season: int | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.source_url.startswith("https://"):
            raise ValueError("provider and HTTPS source_url are required")
        if not self.intended_use.strip():
            raise ValueError("intended_use is required")
        if self.earliest_supported_season is not None and self.earliest_supported_season < 1950:
            raise ValueError("earliest_supported_season must be a valid F1 season")


SOURCE_REGISTRY = {
    "FastF1": SourceRegistryEntry(
        provider="FastF1",
        source_url="https://docs.fastf1.dev/",
        intended_use="Historical session timing, laps, stints, weather, and telemetry.",
        approved_for_ingestion=False,
        attribution_required=True,
    ),
    "OpenF1": SourceRegistryEntry(
        provider="OpenF1",
        source_url="https://openf1.org/docs/",
        intended_use="Recent session laps, stints, pits, and race-control context.",
        approved_for_ingestion=False,
        attribution_required=True,
        earliest_supported_season=2023,
    ),
    "Open-Meteo": SourceRegistryEntry(
        provider="Open-Meteo",
        source_url="https://open-meteo.com/en/docs",
        intended_use="Forecast and historical weather inputs with timestamped availability.",
        approved_for_ingestion=False,
        attribution_required=True,
    ),
}


def approved_source(provider: str) -> SourceRegistryEntry:
    """Return a reviewed source or refuse ingestion before any network call."""
    try:
        entry = SOURCE_REGISTRY[provider]
    except KeyError as error:
        raise ValueError(f"provider {provider!r} is not registered") from error
    if not entry.approved_for_ingestion:
        raise PermissionError(f"{provider} is not approved for ingestion")
    return entry


@dataclass(frozen=True)
class DatasetManifest:
    """Immutable evidence needed to reproduce a cached dataset or replay.

    ``available_at`` is the latest time at which this data may be used in a
    decision replay.  It must not be after the decision timestamp supplied by
    the replay layer.
    """

    dataset_id: str
    provider: str
    source_url: str
    retrieved_at: datetime
    available_at: datetime
    content_sha256: str
    transform_version: str
    data_mode: str

    def __post_init__(self) -> None:
        if not self.dataset_id.strip() or not self.transform_version.strip():
            raise ValueError("dataset_id and transform_version are required")
        if not self.source_url.startswith("https://"):
            raise ValueError("source_url must use HTTPS")
        if self.retrieved_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("timestamps must be timezone-aware")
        if self.available_at > self.retrieved_at:
            raise ValueError("available_at cannot be after retrieved_at")
        if not _SHA256.fullmatch(self.content_sha256):
            raise ValueError("content_sha256 must be a lowercase SHA-256 digest")
        if self.data_mode not in _DATA_MODES:
            raise ValueError("data_mode is not recognised")

    @classmethod
    def from_bytes(
        cls,
        *,
        dataset_id: str,
        provider: str,
        source_url: str,
        retrieved_at: datetime,
        available_at: datetime,
        content: bytes,
        transform_version: str,
        data_mode: str,
    ) -> "DatasetManifest":
        """Build a manifest without exposing a mutable, caller-supplied hash."""
        return cls(
            dataset_id=dataset_id,
            provider=provider,
            source_url=source_url,
            retrieved_at=retrieved_at,
            available_at=available_at,
            content_sha256=sha256(content).hexdigest(),
            transform_version=transform_version,
            data_mode=data_mode,
        )


def assert_available_for_decision(manifest: DatasetManifest, decision_at: datetime) -> None:
    """Reject information that was unavailable at a simulated decision point.

    Historical replay code must call this before a dataset contributes any
    feature.  This deliberately fails closed: a naive timestamp is not enough
    evidence to establish that an input was known at the time.
    """
    if decision_at.tzinfo is None:
        raise ValueError("decision_at must be timezone-aware")
    if manifest.available_at > decision_at:
        raise ValueError(
            f"dataset {manifest.dataset_id!r} was not available at the replay decision time"
        )
