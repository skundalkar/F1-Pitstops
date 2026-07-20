"""Portable, deterministic scenario snapshots for sharing and replaying a brief."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from .strategy import StrategyInputs


@dataclass(frozen=True)
class RaceScenarioSnapshot:
    """The minimum immutable context required to reproduce a strategy brief."""

    race: str
    lineup: tuple[str, ...]
    focus_driver: str
    inputs: StrategyInputs
    data_mode: str
    source_label: str
    source_detail: str
    as_of: str
    disclaimer: str
    version: int = 2

    def __post_init__(self) -> None:
        if self.version != 2:
            raise ValueError("unsupported snapshot version")
        if not self.race.strip():
            raise ValueError("race must not be empty")
        if not self.lineup or len(self.lineup) > 5:
            raise ValueError("lineup must contain between 1 and 5 drivers")
        if len(set(self.lineup)) != len(self.lineup):
            raise ValueError("lineup must not contain duplicate drivers")
        if any(not driver.strip() for driver in self.lineup):
            raise ValueError("lineup drivers must not be empty")
        if self.focus_driver not in self.lineup:
            raise ValueError("focus_driver must be in lineup")
        for field in ("data_mode", "source_label", "source_detail", "as_of", "disclaimer"):
            if not getattr(self, field).strip():
                raise ValueError(f"{field} must not be empty")


def encode_snapshot(snapshot: RaceScenarioSnapshot) -> str:
    """Serialize a snapshot to stable, compact JSON suitable for a share link."""
    payload = {
        "as_of": snapshot.as_of,
        "data_mode": snapshot.data_mode,
        "disclaimer": snapshot.disclaimer,
        "focus_driver": snapshot.focus_driver,
        "inputs": asdict(snapshot.inputs),
        "lineup": list(snapshot.lineup),
        "race": snapshot.race,
        "source_detail": snapshot.source_detail,
        "source_label": snapshot.source_label,
        "version": snapshot.version,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def decode_snapshot(encoded: str) -> RaceScenarioSnapshot:
    """Parse and fully validate JSON emitted by :func:`encode_snapshot`."""
    try:
        payload = json.loads(encoded)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("snapshot must be valid JSON") from error
    if not isinstance(payload, dict):
        raise ValueError("snapshot must be a JSON object")
    expected = {
        "as_of",
        "data_mode",
        "disclaimer",
        "focus_driver",
        "inputs",
        "lineup",
        "race",
        "source_detail",
        "source_label",
        "version",
    }
    if set(payload) != expected:
        raise ValueError("snapshot has an unexpected schema")
    if not isinstance(payload["lineup"], list) or not isinstance(payload["inputs"], dict):
        raise ValueError("snapshot lineup and inputs have invalid types")
    try:
        return RaceScenarioSnapshot(
            race=payload["race"],
            lineup=tuple(payload["lineup"]),
            focus_driver=payload["focus_driver"],
            inputs=StrategyInputs(**payload["inputs"]),
            data_mode=payload["data_mode"],
            source_label=payload["source_label"],
            source_detail=payload["source_detail"],
            as_of=payload["as_of"],
            disclaimer=payload["disclaimer"],
            version=payload["version"],
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"invalid snapshot: {error}") from error
