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
        with self.assertRaises(ValueError):
            StrategyInputs(grid_position=21)
        with self.assertRaises(ValueError):
            StrategyInputs(traffic_context="jammed")

    def test_traffic_and_grid_position_change_aggressive_call(self) -> None:
        clear_air = recommend_strategies(
            StrategyInputs(grid_position=3, traffic_context="clean_air")
        )[2]
        traffic = recommend_strategies(
            StrategyInputs(grid_position=16, traffic_context="traffic")
        )[2]

        self.assertIn("late end", clear_air.pit_windows[0])
        self.assertIn("early end", traffic.pit_windows[0])
        self.assertIn("starting P3", clear_air.why_changed)
        self.assertIn("starting P16", traffic.why_changed)

    def test_explicit_dry_condition_and_starting_compound_bind_all_plans(self) -> None:
        plans = recommend_strategies(
            StrategyInputs(
                race_condition="dry",
                starting_compound="Soft",
                usable_compounds=("Soft", "Medium", "Hard"),
            )
        )

        self.assertTrue(all(plan.is_feasible for plan in plans))
        self.assertTrue(all(plan.tyre_stints[0] == "Soft" for plan in plans))

    def test_unavailable_compound_yields_explanation_and_feasible_alternative(self) -> None:
        plans = recommend_strategies(
            StrategyInputs(
                race_condition="dry",
                starting_compound="Medium",
                usable_compounds=("Soft", "Medium"),
            )
        )
        conservative = plans[0]

        self.assertFalse(conservative.is_feasible)
        self.assertEqual(conservative.tyre_stints, ())
        self.assertIn("Hard", conservative.feasibility_note)
        self.assertEqual(conservative.feasible_alternative, "Feasible alternative: Medium → Soft.")

    def test_rejects_start_compound_incompatible_with_explicit_condition(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot start a dry"):
            recommend_strategies(
                StrategyInputs(race_condition="dry", starting_compound="Intermediate")
            )


if __name__ == "__main__":
    unittest.main()
