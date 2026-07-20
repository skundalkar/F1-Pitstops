from data_sources import TyreCompound, load_seed_weekend
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
