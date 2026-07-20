# Product Governance

## M1 acceptance findings

Independent review of the initial playable brief identified three gaps that
prevent M1 from being treated as a complete customer-ready slice:

1. **Lineup-to-plan connection:** selecting drivers changes outlook cards, but
   the strategy board is still driven by one generic grid-position control.
   A user cannot yet obtain a recommendation for a chosen driver.
2. **Single source of strategy truth:** the Streamlit UI contains a separate
   heuristic implementation rather than rendering the tested
   `pitwall.strategy` recommendations. This risks divergent user-visible
   behaviour and test coverage.
3. **Reproducible sharing:** save/reload and a shareable assumptions snapshot
   are required for a teammate brief, but are not yet implemented. A viewer
   cannot reconstruct the same race plan in a clean session.

M1 remains a validated prototype, not a completed product milestone. The
findings above are intentionally recorded as product acceptance gaps rather
than defects in the seed-data demonstration.

## Active next milestone — Personal Race Brief

**Outcome:** an enthusiast can create a driver-specific pre-race plan, reopen
it locally, and share a reproducible, clearly labelled seed-data brief.

### Acceptance criteria

- A user selects a focus driver from their lineup; that driver’s grid context
  materially informs the recommendation, its rationale, or its trigger.
- The strategy board renders recommendations from `pitwall.strategy`; there is
  no competing recommendation implementation in the UI.
- The brief captures the selected race, lineup, focus driver, scenario inputs,
  primary and alternative plans, data mode/source, timestamp, and educational
  disclaimer.
- A locally saved brief is restored offline after reload.
- A versioned share snapshot, via canonical URL parameters and/or a portable
  JSON/Markdown export, reconstructs the same plan in a clean session.
- Invalid or obsolete snapshot fields are handled safely and visibly, without
  silently changing the plan.
- Deterministic tests cover plan-input mapping and snapshot validation; browser
  acceptance covers creating, reopening, and sharing a plan.

## Independent milestone reviews

Before any milestone is marked complete, two independent reviews are required:

- **Pitwall Principal:** checks strategic credibility: every visible call has
  assumptions, uncertainty, trade-offs, and a condition that changes the call;
  data provenance and limitations are explicit; no claim exceeds the evidence.
- **Experience Designer:** checks that the primary user flow is understandable
  without expert knowledge, decisions are actionable, labels are accessible,
  and the interface does not bury material uncertainty or state changes.

Each reviewer records a pass, conditional pass with named follow-ups, or fail
in `docs/verification.md`. A conditional pass cannot mark the milestone
complete until its named follow-ups are closed. The implementation author does
not self-certify either review.
