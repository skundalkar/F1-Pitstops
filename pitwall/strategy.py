"""A deliberately transparent first-cut Formula 1 race strategy recommender.

This module is a rules-based baseline, not a prediction of an actual team call.
Its value is that every recommendation can be inspected, tested, and replaced by
better calibrated models as the project gains data.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyInputs:
    """Pre-race assumptions, represented as simple, user-adjustable values.

    Values expressed as a chance or emphasis must be between zero and one.
    ``degradation`` is low, medium, or high. ``pit_loss_seconds`` is the total
    expected time lost for one green-flag pit stop.
    """

    degradation: str = "medium"
    safety_car_chance: float = 0.35
    rain_likelihood: float = 0.10
    pit_loss_seconds: float = 22.0
    track_position_emphasis: float = 0.50
    grid_position: int = 10
    traffic_context: str = "neutral"

    def __post_init__(self) -> None:
        if self.degradation not in {"low", "medium", "high"}:
            raise ValueError("degradation must be low, medium, or high")
        for name, value in (
            ("safety_car_chance", self.safety_car_chance),
            ("rain_likelihood", self.rain_likelihood),
            ("track_position_emphasis", self.track_position_emphasis),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.pit_loss_seconds <= 0:
            raise ValueError("pit_loss_seconds must be positive")
        if not 1 <= self.grid_position <= 20:
            raise ValueError("grid_position must be between 1 and 20")
        if self.traffic_context not in {"traffic", "neutral", "clean_air"}:
            raise ValueError("traffic_context must be traffic, neutral, or clean_air")


@dataclass(frozen=True)
class StrategyPlan:
    """A recommendation and the decision context that makes it suitable."""

    name: str
    tyre_stints: tuple[str, ...]
    pit_windows: tuple[str, ...]
    tradeoffs: tuple[str, ...]
    invalidating_trigger: str
    why_changed: str


def recommend_strategies(inputs: StrategyInputs) -> tuple[StrategyPlan, ...]:
    """Return conservative, balanced, and aggressive plans in that order."""

    wet = inputs.rain_likelihood >= 0.45
    conservative = _conservative(inputs, wet)
    balanced = _balanced(inputs, wet)
    aggressive = _aggressive(inputs, wet)
    return conservative, balanced, aggressive


def _conservative(inputs: StrategyInputs, wet: bool) -> StrategyPlan:
    if wet:
        stints = ("Intermediate", "Intermediate")
        windows = ("Reassess at lap 18–26; pit only for clear crossover",)
        trigger = "A sustained dry line appears and slicks are at least 1.5s/lap quicker."
    elif inputs.degradation == "high":
        stints = ("Medium", "Hard", "Hard")
        windows = ("Lap 14–20", "Lap 36–43")
        trigger = "A Safety Car before lap 12 makes a two-stop plan preferable."
    else:
        stints = ("Medium", "Hard")
        windows = (_window("Lap 25–33", inputs, aggressive=False),)
        trigger = "Tyre fall-off exceeds the expected pace loss before lap 20."
    return StrategyPlan(
        name="Conservative",
        tyre_stints=stints,
        pit_windows=windows,
        tradeoffs=(
            "Protects tyre life and reduces exposure to an early stop.",
            "Gives up some short-run pace to preserve a dependable finish.",
            _context_tradeoff(inputs, aggressive=False),
        ),
        invalidating_trigger=trigger,
        why_changed=_why_changed(inputs, "conservative", wet),
    )


def _balanced(inputs: StrategyInputs, wet: bool) -> StrategyPlan:
    if wet:
        stints = ("Intermediate", "Intermediate", "Soft")
        windows = ("Lap 16–24 if rain eases", "Lap 38–46 if track is dry")
        trigger = "Rain intensity increases enough that full wets become required."
    elif inputs.degradation == "high":
        stints = ("Medium", "Hard", "Medium")
        windows = ("Lap 16–22", "Lap 39–46")
        trigger = "A late Safety Car after lap 42 makes a soft-tyre finish stronger."
    else:
        stints = ("Medium", "Hard")
        windows = (_window("Lap 22–29", inputs, aggressive=False),)
        trigger = "An undercut opportunity opens with more than 1.0s of clear air."
    return StrategyPlan(
        name="Balanced",
        tyre_stints=stints,
        pit_windows=windows,
        tradeoffs=(
            "Balances track position with enough tyre performance to react.",
            "Needs clean air after the stop to realise its pace advantage.",
            _context_tradeoff(inputs, aggressive=False),
        ),
        invalidating_trigger=trigger,
        why_changed=_why_changed(inputs, "balanced", wet),
    )


def _aggressive(inputs: StrategyInputs, wet: bool) -> StrategyPlan:
    if wet:
        stints = ("Intermediate", "Soft", "Soft")
        windows = ("Pit at the earliest safe slick crossover", "Lap 39–47")
        trigger = "Rain returns before the second stop or slick crossover is uncertain."
    elif inputs.degradation == "high":
        stints = ("Soft", "Medium", "Soft")
        windows = ("Lap 10–16", "Lap 37–44")
        trigger = "Early degradation prevents the first stint reaching lap 10."
    else:
        stints = ("Soft", "Hard")
        windows = (_window("Lap 14–21", inputs, aggressive=True),)
        trigger = "Traffic after the early stop removes the undercut benefit."
    return StrategyPlan(
        name="Aggressive",
        tyre_stints=stints,
        pit_windows=windows,
        tradeoffs=(
            "Chases early track-position gains and an undercut opportunity.",
            "Pays greater tyre-life and traffic risk if the race stays green.",
            _context_tradeoff(inputs, aggressive=True),
        ),
        invalidating_trigger=trigger,
        why_changed=_why_changed(inputs, "aggressive", wet),
    )


def _why_changed(inputs: StrategyInputs, style: str, wet: bool) -> str:
    reasons: list[str] = []
    if wet:
        reasons.append("Rain likelihood is high, so crossover flexibility matters most")
    else:
        reasons.append(f"{inputs.degradation.capitalize()} degradation sets the tyre-life baseline")
    if inputs.safety_car_chance >= 0.50:
        reasons.append("a likely Safety Car increases the value of keeping options open")
    if inputs.pit_loss_seconds >= 25:
        reasons.append("a costly pit lane rewards fewer planned stops")
    if inputs.track_position_emphasis >= 0.70:
        reasons.append("track position is weighted heavily")
    if inputs.traffic_context == "traffic":
        reasons.append("traffic makes an early undercut and clean-air release more valuable")
    elif inputs.traffic_context == "clean_air":
        reasons.append("clean air supports extending the current stint")
    if inputs.grid_position <= 5:
        reasons.append(f"starting P{inputs.grid_position} increases the cost of surrendering track position")
    elif inputs.grid_position >= 13:
        reasons.append(f"starting P{inputs.grid_position} creates upside from an offset strategy")
    elif style == "aggressive":
        reasons.append("the aggressive option still assumes clear air can unlock an undercut")
    return "; ".join(reasons) + "."


def _window(base_window: str, inputs: StrategyInputs, aggressive: bool) -> str:
    """Annotate a static baseline window with the relevant track-position call."""
    if inputs.traffic_context == "traffic" and aggressive:
        return f"{base_window}; favour the early end to release into clean air"
    if inputs.traffic_context == "clean_air" or inputs.grid_position <= 5:
        return f"{base_window}; favour the late end while track position is protected"
    if inputs.grid_position >= 13 and aggressive:
        return f"{base_window}; use the early end to seek an undercut"
    return base_window


def _context_tradeoff(inputs: StrategyInputs, aggressive: bool) -> str:
    if inputs.traffic_context == "traffic" and aggressive:
        return "Traffic ahead makes the early stop worthwhile only if the release gap is clear."
    if inputs.traffic_context == "clean_air":
        return "Clean air makes preserving the current stint more valuable than forcing an undercut."
    if inputs.grid_position <= 5:
        return "A front-five start makes defending track position more valuable than a speculative stop."
    if inputs.grid_position >= 13:
        return "A lower-grid start makes an offset call worthwhile if it avoids the midfield pit queue."
    return "A midfield start keeps both track-position and tyre-offset options open."
