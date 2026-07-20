import json

import pytest

from data_sources import SeedFixtureError, TyreCompound, load_offline_race_brief, load_seed_weekend
from data_sources.providers import FastF1Source, OpenF1Source, OpenMeteoSource, SourceNotConfigured


def test_seed_weekend_is_offline_and_repeatable():
    weekend = load_seed_weekend()

    assert weekend.data_mode == "offline_seed"
    assert weekend.event_name == "Pitwall Demo Grand Prix"
    assert len(weekend.drivers) == 5
    assert weekend.drivers[0].available_compounds == (
        TyreCompound.SOFT,
        TyreCompound.MEDIUM,
        TyreCompound.HARD,
    )
    assert weekend.weather.rain_probability == 0.25


def test_provider_stubs_cannot_trigger_implicit_ingestion():
    for source in (FastF1Source(), OpenF1Source(), OpenMeteoSource()):
        try:
            source.fetch_weekend(2026, 1)
        except SourceNotConfigured as error:
            assert source.provider_name in str(error)
        else:
            raise AssertionError("provider stub unexpectedly fetched data")


def test_offline_brief_exposes_fixed_provenance_and_freshness():
    brief = load_offline_race_brief()

    assert brief.weekend.data_mode == "offline_seed"
    assert brief.provenance.is_live is False
    assert brief.provenance.dataset == "bundled offline demo fixture"
    assert brief.freshness.label == "Offline demo data"
    assert brief.freshness.as_of == brief.provenance.retrieved_at


def test_missing_fixture_field_has_actionable_validation_error(tmp_path):
    malformed_fixture = tmp_path / "missing-weather.json"
    malformed_fixture.write_text(json.dumps({"season": 2026}), encoding="utf-8")

    with pytest.raises(SeedFixtureError, match="Missing required field 'drivers'"):
        load_seed_weekend(malformed_fixture)
