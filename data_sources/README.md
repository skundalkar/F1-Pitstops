# Public data adapters

The app defaults to [`fixtures/sample_race_weekend.json`](fixtures/sample_race_weekend.json), a deterministic offline demo. It is illustrative, not historical F1 data, and is deliberately small so local development does not trigger bulk downloads.

Provider adapters are boundary stubs only:

| Provider | Intended use | Activation rule |
| --- | --- | --- |
| FastF1 | historical laps, stints, timing, telemetry | explicit ingestion/cache job |
| OpenF1 | live/recent laps, stints, pit stops, race control | explicitly enabled live refresh |
| Open-Meteo | forecast and historical weather | explicitly enabled forecast refresh |

All adapters must normalize to `RaceWeekend`, record source timestamps/URLs, and preserve source attribution. Provider coverage and terms must be reviewed before public release. No page render may silently call a provider.
