import unittest

from pitwall.strategy import StrategyInputs, recommend_strategies


class StrategyRecommendationTests(unittest.TestCase):
    def test_returns_three_named_explainable_plans(self) -> None:
        plans = recommend_strategies(StrategyInputs())

        self.assertEqual([plan.name for plan in plans], ["Conservative", "Balanced", "Aggressive"])
        for plan in plans:
            self.assertTrue(plan.tyre_stints)
            self.assertTrue(plan.pit_windows)
            self.assertTrue(plan.tradeoffs)
            self.assertTrue(plan.invalidating_trigger)
            self.assertTrue(plan.why_changed)

    def test_high_degradation_uses_three_stints_for_all_plans(self) -> None:
        plans = recommend_strategies(StrategyInputs(degradation="high"))

        self.assertTrue(all(len(plan.tyre_stints) == 3 for plan in plans))

    def test_rain_plan_prioritises_intermediates_and_crossover(self) -> None:
        plans = recommend_strategies(StrategyInputs(rain_likelihood=0.70))

        self.assertEqual(plans[0].tyre_stints[0], "Intermediate")
        self.assertIn("Rain likelihood is high", plans[1].why_changed)

    def test_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            StrategyInputs(degradation="extreme")
        with self.assertRaises(ValueError):
            StrategyInputs(safety_car_chance=1.1)
        with self.assertRaises(ValueError):
            StrategyInputs(pit_loss_seconds=0)


if __name__ == "__main__":
    unittest.main()
