# Project Plan

## Operating cadence

Each work slice follows: define acceptance criteria → implement → unit test →
browser acceptance test where UI changes → review → small commit → push.

Commits are capability-based, usually one per completed vertical slice. A commit
must not mix unrelated data, UI, and refactoring work. `main` is the private
working branch initially; change to protected branches and pull requests when
teammates begin contributing.

## Milestones

| Milestone | Outcome | Exit criteria |
|---|---|---|
| M0 — Foundation | Repository, contracts, strategy baseline | Clean install, tests pass, docs committed |
| M1 — Playable brief | Local Streamlit race/lineup/scenario app | Core flow browser-tested; seed data works offline |
| M2 — Historical lab | Narrow, sourced historical replay | Ingestion is explicit and backtests avoid future data |
| M3 — Live companion | Public-data second screen | Freshness, gaps, and recompute triggers are visible |
| M4 — Shareable product | Private shared race briefs | Stable share/export, provenance, and privacy review |

## Progress dashboard

The in-app dashboard will report:

- Milestone completion and current work item.
- Data-source coverage, freshness, and offline/online status.
- Test status: unit, integration, and browser acceptance.
- Model/strategy maturity: seed rules, backtested rules, or live estimate.
- Known limitations and next decision.

## Quality gates

1. Run the complete Python test suite on every logic change.
2. Browser-test the primary flow for every UI change: load app, choose lineup,
   alter a scenario, and confirm recommendations/explanations update.
3. Review all displayed recommendations against the Pitwall Principal checklist:
   plan, risk, trigger, assumptions, and uncertainty.
4. Record screenshots or an acceptance note in the project log for milestone
   completion.
5. Do not bulk-ingest historical data until data source and licensing checks are
   recorded.

## Tonight's target

Deliver M1's initial playable skeleton: seeded race brief, lineup picker,
editable strategy scenarios, and transparent recommendations. The next work
item is the milestone/progress screen and browser acceptance coverage.
