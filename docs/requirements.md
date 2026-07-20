# Requirements

## Product intent

Pitwall Planner is a private, enthusiast-first Formula 1 decision-support tool.
It helps users build a driver lineup, understand an upcoming race, compare tyre
and pit strategies, and later reconsider plans as the race changes. It uses
public data and must make uncertainty and missing inputs visible.

## Functional requirements

### Pre-race brief (M1)

- Show the selected race, circuit characteristics, forecast, pit-lane loss,
  available compounds, and strategic watch-outs.
- Show source/provenance and last-updated time for factual inputs.
- Label estimates and unavailable inputs clearly.
- Explain likely stop-count range and whether track position or fresh tyres is
  the central trade-off.

### Lineup and driver context (M1)

- Allow a user to select up to five drivers from a supplied grid.
- Show each selected driver's grid context, strategy opportunity, risk, likely
  plan, and alternative plan.
- Preserve the selected lineup locally.

### Scenario comparison (M1)

- Allow editing of degradation, Safety Car likelihood, rain likelihood,
  pit-lane loss, and track-position emphasis.
- Produce conservative, balanced, and aggressive plans.
- For every plan, show tyre sequence, pit window, trade-offs, invalidating
  trigger, and why it changed.

### Historical learning (M2)

- Load a narrow, validated historical dataset by explicit user action.
- Compare current race context with similar past races without implying
  causation from simple averages.
- Replay a historical race from pre-race information only.

### Live companion (M3)

- Display data freshness, source health, and clearly labelled delayed/manual
  refresh status.
- Recalculate scenario plans after Safety Car, VSC, rain, rival-pit, red-flag,
  or retirement events.
- Preserve a timeline of assumptions and recommendation changes.

## Non-functional requirements

- **Explainability:** no recommendation may appear without assumptions, risk,
  and a condition that would change it.
- **Honesty:** show probabilities/ranges; never imply official team access or
  guaranteed finishing positions.
- **Data integrity:** reproduce every displayed result from recorded inputs,
  source, and timestamp.
- **Privacy:** v1 is local/private by default; do not send user lineups to a
  third party.
- **Performance:** M1 interactions should update within two seconds on a local
  machine using the seed dataset.
- **Resilience:** the app remains usable offline with deterministic seed data.
- **Accessibility:** keyboard-usable controls, readable labels, and colour is
  never the sole carrier of meaning.
- **Testability:** deterministic logic has unit tests; user-critical flows have
  browser-level acceptance tests.
- **Maintainability:** separate data adapters, strategy logic, and UI; commit
  small coherent slices with clear tests.

## Explicit constraint

> **Strategy simulator — educational estimate, not official team strategy.**
> Recommendations use public data and scenario assumptions; live race events,
> tyre condition, traffic, and team information can materially change the
> optimal call.
