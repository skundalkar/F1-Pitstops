# Product Design

## System architecture

```mermaid
flowchart LR
  P[Public sources\nFastF1 · OpenF1 · Open-Meteo] --> A[Explicit data adapters]
  S[Offline seed fixture] --> A
  A --> C[Race-context contract\nsource + timestamp + confidence]
  C --> E[Explainable strategy engine]
  E --> U[Streamlit experience]
  U --> B[Race brief]
  U --> L[Lineup builder]
  U --> X[Scenario comparison]
  E --> R[Recommendation audit trail]
```

The app starts from a deterministic offline fixture. Future providers are opt-in:
the app must display the active source and timestamp before showing an estimate.

## Data model

```mermaid
erDiagram
  RACE_WEEKEND ||--|| CIRCUIT : occurs_at
  RACE_WEEKEND ||--o{ SESSION : includes
  SESSION ||--o{ DRIVER_CONTEXT : has
  DRIVER_CONTEXT ||--o{ TYRE_STINT : uses
  DRIVER_CONTEXT ||--o{ PIT_EVENT : makes
  RACE_WEEKEND ||--o{ WEATHER_SAMPLE : observes
  RACE_WEEKEND ||--o{ STRATEGY_SCENARIO : evaluates
  STRATEGY_SCENARIO ||--o{ STRATEGY_PLAN : produces
  DRIVER_CONTEXT {
    string driver_id
    string team
    int grid_position
    string source
    datetime observed_at
  }
  STRATEGY_SCENARIO {
    float rain_likelihood
    float safety_car_chance
    string degradation
    float pit_loss_seconds
  }
  STRATEGY_PLAN {
    string plan_type
    string tyre_sequence
    string pit_window
    string risk
    string invalidating_trigger
  }
```

## User personas

### The Saturday strategist — primary

An informed F1 enthusiast preparing for a race weekend. They want a short,
credible brief first, then the freedom to test a bold call. They distrust opaque
predictions and value a clear explanation of uncertainty.

### The lineup captain

A small group’s fantasy/competition organiser. They choose up to five drivers,
compare upside with reliability, and share a brief with friends. They need a
stable snapshot of assumptions, not a copied third-party fantasy game.

### The live second-screen fan — later

Watches a race and wants the strategic consequence of a Safety Car, rain shower,
or rival pit stop without pretending to replace a real pit wall. They need speed,
freshness labels, and a concise "pit now / wait / hedge" comparison.

## Core user flows

### Build and share a pre-race plan

```mermaid
flowchart LR
  A[Open race brief] --> B[Read circuit + conditions]
  B --> C[Select up to five drivers]
  C --> D[Inspect driver risks and opportunities]
  D --> E[Adjust weather / degradation / Safety Car assumptions]
  E --> F[Compare three plans]
  F --> G[Read risks and invalidating triggers]
  G --> H[Save or share assumptions snapshot]
```

### Challenge a strategy

```mermaid
flowchart LR
  A[Choose a driver] --> B[Start from balanced plan]
  B --> C[Change one scenario assumption]
  C --> D[Review what changed]
  D --> E{Trade-off understood?}
  E -- No --> C
  E -- Yes --> F[Keep conditional plan]
```

### Live replan — M3

```mermaid
flowchart LR
  A[Event arrives] --> B[Confirm source freshness]
  B --> C[Update race state]
  C --> D[Compare pit now / wait / hedge]
  D --> E[Show expected gain, risk, and trigger]
  E --> F[Record recommendation timeline]
```

## Interaction rules

- Lead with the recommendation; put evidence and history one step deeper.
- Every plan must show tyre sequence, pit window, upside, risk, and invalidating
  trigger together.
- Use probability bands/ranges; avoid single-position certainty.
- Clearly distinguish confirmed inputs, estimates, and unavailable data.
- Keep scenario controls limited to inputs that materially change a pit call.

## Nice-to-have backlog

- Historical comparable-race explorer and replay.
- Animated circuit/stint timeline and shareable short simulation clip.
- Saved named scenarios and shareable read-only race briefs.
- Live decision timeline with "what changed?" explanations.
- Accessibility preferences and compact second-screen mode.
- Personal performance journal: compare user calls to the eventual race.
- Private teammate spaces, comments, and versioned strategy briefs.
