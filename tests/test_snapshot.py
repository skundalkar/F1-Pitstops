import unittest

from pitwall.snapshot import RaceScenarioSnapshot, decode_snapshot, encode_snapshot
from pitwall.strategy import StrategyInputs


class RaceScenarioSnapshotTests(unittest.TestCase):
    def test_round_trip_is_deterministic(self) -> None:
        snapshot = RaceScenarioSnapshot(
            race="2026 British Grand Prix",
            lineup=("Lando Norris", "George Russell"),
            focus_driver="Lando Norris",
            inputs=StrategyInputs(grid_position=2, traffic_context="clean_air"),
            data_mode="offline_seed",
            source_label="Offline demo data",
            source_detail="Illustrative fixture; no live or historical provider was queried.",
            as_of="2026-01-01T00:00:00+00:00",
            disclaimer="Educational estimate; not official team strategy.",
        )

        encoded = encode_snapshot(snapshot)
        self.assertEqual(encoded, encode_snapshot(snapshot))
        self.assertEqual(decode_snapshot(encoded), snapshot)

    def test_rejects_schema_and_focus_driver_errors(self) -> None:
        with self.assertRaises(ValueError):
            RaceScenarioSnapshot(
                race="Test GP",
                lineup=("Driver One",),
                focus_driver="Driver Two",
                inputs=StrategyInputs(),
                data_mode="offline_seed",
                source_label="Offline demo data",
                source_detail="Illustrative fixture; no provider was queried.",
                as_of="2026-01-01T00:00:00+00:00",
                disclaimer="Educational estimate; not official team strategy.",
            )
        with self.assertRaises(ValueError):
            decode_snapshot('{"race":"Test"}')


if __name__ == "__main__":
    unittest.main()
