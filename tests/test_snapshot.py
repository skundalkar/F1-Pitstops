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
            )
        with self.assertRaises(ValueError):
            decode_snapshot('{"race":"Test"}')


if __name__ == "__main__":
    unittest.main()
