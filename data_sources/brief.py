"""App-facing offline race brief mapper.

The values below are intentionally fixed: the demo must not pretend to become
fresher merely because somebody opened the page later in the day.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .contracts import DataFreshness, DataProvenance, RaceBrief, RaceWeekend
from .seed import SEED_WEEKEND_PATH, load_seed_weekend

_DEMO_AS_OF = datetime(2026, 1, 1, tzinfo=timezone.utc)


def map_offline_weekend_to_brief(weekend: RaceWeekend) -> RaceBrief:
    """Attach unambiguous demo provenance and freshness to an offline weekend."""
    if weekend.data_mode != "offline_seed":
        raise ValueError("Offline brief mapper accepts only an offline_seed weekend")
    return RaceBrief(
        weekend=weekend,
        provenance=DataProvenance(
            provider="Pitwall Planner",
            dataset="bundled offline demo fixture",
            source_url=None,
            retrieved_at=_DEMO_AS_OF,
            is_live=False,
        ),
        freshness=DataFreshness(
            label="Offline demo data",
            detail="Illustrative fixture; no live or historical provider was queried.",
            as_of=_DEMO_AS_OF,
        ),
    )


def load_offline_race_brief(path: Path = SEED_WEEKEND_PATH) -> RaceBrief:
    """Load the bundled fixture and return the app-ready, typed briefing payload."""
    return map_offline_weekend_to_brief(load_seed_weekend(path))
