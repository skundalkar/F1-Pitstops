from datetime import datetime, timedelta, timezone

import pytest

from data_sources.registry import (
    DatasetManifest,
    SOURCE_REGISTRY,
    approved_source,
    assert_available_for_decision,
)


NOW = datetime(2026, 7, 20, tzinfo=timezone.utc)


def test_registry_refuses_unapproved_or_unknown_ingestion():
    assert {"FastF1", "OpenF1", "Open-Meteo"} <= set(SOURCE_REGISTRY)

    with pytest.raises(PermissionError, match="not approved"):
        approved_source("FastF1")
    with pytest.raises(ValueError, match="not registered"):
        approved_source("Unknown")


def test_manifest_hashes_content_and_records_replay_time_boundary():
    manifest = DatasetManifest.from_bytes(
        dataset_id="fastf1-2024-01-race-raw",
        provider="FastF1",
        source_url="https://docs.fastf1.dev/",
        retrieved_at=NOW,
        available_at=NOW - timedelta(minutes=5),
        content=b'{"session":"race"}',
        transform_version="raw-v1",
        data_mode="historical_replay",
    )

    assert manifest.content_sha256 == "ff24299086994ee8fb89b2bc96e11190305e202f9c545f6ef7169934c4046521"
    assert manifest.available_at <= manifest.retrieved_at


def test_manifest_rejects_leaky_or_unverifiable_provenance():
    with pytest.raises(ValueError, match="available_at"):
        DatasetManifest.from_bytes(
            dataset_id="bad",
            provider="FastF1",
            source_url="https://docs.fastf1.dev/",
            retrieved_at=NOW,
            available_at=NOW + timedelta(seconds=1),
            content=b"raw",
            transform_version="raw-v1",
            data_mode="historical_replay",
        )


def test_replay_refuses_a_snapshot_not_available_at_decision_time():
    manifest = DatasetManifest.from_bytes(
        dataset_id="weather-2024-01-forecast",
        provider="Open-Meteo",
        source_url="https://open-meteo.com/en/docs",
        retrieved_at=NOW,
        available_at=NOW - timedelta(minutes=5),
        content=b"forecast",
        transform_version="raw-v1",
        data_mode="historical_replay",
    )

    assert_available_for_decision(manifest, NOW)
    with pytest.raises(ValueError, match="not available"):
        assert_available_for_decision(manifest, NOW - timedelta(minutes=10))
    with pytest.raises(ValueError, match="timezone-aware"):
        assert_available_for_decision(manifest, datetime(2026, 7, 20))
    with pytest.raises(ValueError, match="timezone-aware"):
        DatasetManifest.from_bytes(
            dataset_id="bad-time",
            provider="FastF1",
            source_url="https://docs.fastf1.dev/",
            retrieved_at=datetime(2026, 1, 1),
            available_at=datetime(2026, 1, 1),
            content=b"raw",
            transform_version="raw-v1",
            data_mode="historical_replay",
        )
