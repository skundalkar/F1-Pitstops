"""Personal Race Brief — a local, explainable F1 strategy sandbox."""

from __future__ import annotations

import html
import re

import streamlit as st

from data_sources import load_offline_race_brief
from pitwall.snapshot import RaceScenarioSnapshot, encode_snapshot
from pitwall.strategy import StrategyInputs, StrategyPlan, recommend_strategies


st.set_page_config(page_title="Pitwall Planner", page_icon="🏁", layout="wide", initial_sidebar_state="expanded")

TEAM_TOKENS = ("#5E81AC", "#B48E5A", "#7A9E7E", "#9A6C91", "#6D8FA0", "#A5795B")


def neutral_team_colour(team: str) -> str:
    """Return a stable product colour, deliberately not a team's official livery colour."""
    return TEAM_TOKENS[sum(ord(character) for character in team) % len(TEAM_TOKENS)]


def initials(name: str) -> str:
    return "".join(part[0] for part in name.split()[:2]).upper()


def first_lap(window: str) -> int | None:
    """Extract a numeric display marker without inventing a lap for a conditional call."""
    match = re.search(r"lap\s+(\d+)", window, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def plan_map(plans: tuple[StrategyPlan, ...], laps: int, focus_driver: str, team: str) -> str:
    """Render an original schematic only; it is not circuit geometry or official artwork."""
    colour = neutral_team_colour(team)
    paths = ["M25 190 C30 60 180 42 275 96 S475 250 580 135 S745 35 830 100 C915 165 895 275 750 286 S530 342 395 278 S150 325 85 275 C42 242 24 220 25 190"]
    y_positions = (82, 128, 174)
    svg = [
        "<svg viewBox='0 0 940 370' role='img' aria-label='Schematic race plan map' xmlns='http://www.w3.org/2000/svg'>",
        "<rect width='940' height='370' rx='18' fill='#10182b'/>",
        "<path d='" + paths[0] + "' fill='none' stroke='#344967' stroke-width='17' stroke-linecap='round'/>",
        "<path d='" + paths[0] + "' fill='none' stroke='#8295ad' stroke-width='2' stroke-dasharray='7 8'/>",
        "<text x='36' y='342' fill='#9fb0c7' font-family='sans-serif' font-size='13'>Original schematic · not to scale</text>",
        "<text x='760' y='342' fill='#9fb0c7' font-family='sans-serif' font-size='13'>Race distance: " + str(laps) + " laps</text>",
    ]
    for index, plan in enumerate(plans):
        y = y_positions[index]
        if not plan.is_feasible:
            svg.extend(
                [
                    f"<rect x='128' y='{y - 17}' width='697' height='34' rx='8' fill='#3c202b' stroke='#d46a7d' stroke-width='1'/>",
                    f"<text x='145' y='{y + 5}' fill='#ffd9df' font-family='sans-serif' font-size='14' font-weight='700'>{html.escape(plan.name)} — unavailable with selected tyres / conditions</text>",
                ]
            )
            continue
        windows = [first_lap(window) for window in plan.pit_windows]
        markers = []
        for marker_index, lap in enumerate(windows):
            if lap is None:
                markers.append(
                    f"<text x='800' y='{y + 5}' text-anchor='end' fill='#f5c451' font-family='sans-serif' font-size='12'>Crossover decision</text>"
                )
                continue
            x = 145 + int(630 * min(lap, laps) / laps)
            markers.append(
                f"<circle cx='{x}' cy='{y}' r='10' fill='{colour}' stroke='#f5c451' stroke-width='3'/>"
                f"<text x='{x}' y='{y + 4}' text-anchor='middle' fill='#0b1020' font-family='sans-serif' font-size='9' font-weight='700'>P{marker_index + 1}</text>"
            )
        svg.extend(
            [
                f"<line x1='128' y1='{y}' x2='825' y2='{y}' stroke='{colour}' stroke-width='3' opacity='{0.9 - index * 0.18}'/>",
                f"<text x='36' y='{y + 5}' fill='#edf2f7' font-family='sans-serif' font-size='15' font-weight='700'>{html.escape(plan.name)}</text>",
                *markers,
            ]
        )
    svg.append(f"<circle cx='100' cy='128' r='16' fill='{colour}'/><text x='100' y='133' text-anchor='middle' fill='white' font-family='sans-serif' font-size='11' font-weight='700'>{html.escape(initials(focus_driver))}</text>")
    svg.append("</svg>")
    return "".join(svg)


def plan_text(plan: StrategyPlan) -> str:
    if not plan.is_feasible:
        return f"{plan.name}: unavailable. {plan.feasibility_note} {plan.feasible_alternative}"
    stops = "; ".join(plan.pit_windows)
    tyres = " → ".join(plan.tyre_stints)
    return f"{plan.name}: {tyres}. Pit window: {stops}. Trigger: {plan.invalidating_trigger}"


def plan_card(plan: StrategyPlan) -> None:
    if not plan.is_feasible:
        st.error(f"{plan.name} is not feasible", icon="⛔")
        st.write(plan.feasibility_note)
        st.success(plan.feasible_alternative, icon="✓")
        return
    st.markdown(f"<div class='plan-card'><div class='eyebrow'>{html.escape(plan.name)}</div><div class='tyres'>{html.escape(' → '.join(plan.tyre_stints))}</div></div>", unsafe_allow_html=True)
    st.markdown("**Pit window**  ")
    st.write(" · ".join(plan.pit_windows))
    st.markdown("**Trade-offs**")
    for tradeoff in plan.tradeoffs:
        st.caption(f"• {tradeoff}")
    st.markdown("**Change trigger**")
    st.info(plan.invalidating_trigger, icon="🔄")


def input_changes(baseline: StrategyInputs, current: StrategyInputs) -> list[str]:
    """Translate snapshot differences into a short, decision-useful comparison."""
    labels = {
        "degradation": ("Tyre degradation", lambda value: value.capitalize()),
        "safety_car_chance": ("Safety Car", lambda value: f"{value:.0%}"),
        "rain_likelihood": ("Rain", lambda value: f"{value:.0%}"),
        "track_position_emphasis": ("Track position", lambda value: f"{value:.0%}"),
        "traffic_context": ("Traffic release", lambda value: value.replace("_", " ").title()),
        "race_condition": ("Race condition", lambda value: value.title()),
        "starting_compound": ("Starting tyre", str),
        "grid_position": ("Fixture grid", lambda value: f"P{value}"),
    }
    changes = []
    for field, (label, display) in labels.items():
        before, after = getattr(baseline, field), getattr(current, field)
        if before != after:
            changes.append(f"**{label}:** {display(before)} → {display(after)}")
    return changes


def plan_changes(baseline: StrategyPlan, current: StrategyPlan) -> list[str]:
    """Summarise only the recommendation changes that alter a pitwall decision."""
    if baseline.is_feasible and not current.is_feasible:
        return [f"Now unavailable — {current.feasibility_note}", current.feasible_alternative]
    if not baseline.is_feasible and current.is_feasible:
        return ["Now feasible with the current tyre and condition selection."]
    if not baseline.is_feasible and not current.is_feasible:
        return ["Still unavailable under both scenarios."]
    changes = []
    if baseline.tyre_stints != current.tyre_stints:
        changes.append(f"Tyres: {' → '.join(baseline.tyre_stints)} → {' → '.join(current.tyre_stints)}")
    if baseline.pit_windows != current.pit_windows:
        changes.append(f"Pit window: {' · '.join(baseline.pit_windows)} → {' · '.join(current.pit_windows)}")
    if baseline.tradeoffs != current.tradeoffs:
        changes.append(f"Trade-off now: {current.tradeoffs[-1]}")
    if baseline.invalidating_trigger != current.invalidating_trigger:
        changes.append(f"Trigger now: {current.invalidating_trigger}")
    if not changes:
        changes.append("No call change — the same tyre sequence, window, and trigger still apply.")
    return changes


brief = load_offline_race_brief()
weekend = brief.weekend
entries = {entry.driver: entry for entry in weekend.drivers}
driver_names = list(entries)

st.markdown(
    """<style>
    .stApp { background: #0b1020; color: #edf2f7; }
    [data-testid="stSidebar"] { background: #10182b; }
    .eyebrow { color: #f5c451; font-size: .78rem; font-weight: 750; letter-spacing: .11em; text-transform: uppercase; }
    .hero { padding: 1rem 0 .25rem; } .hero h1 { font-size: 2.45rem; margin: .15rem 0; }
    .hero p { color: #b7c3d3; font-size: 1.05rem; max-width: 48rem; }
    .identity { display:flex; align-items:center; gap:.75rem; margin:.4rem 0 1.1rem; }
    .avatar { width:46px; height:46px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-weight:800; }
    .team-token { font-size:.82rem; color:#b7c3d3; }
    .plan-card { background:#151f35; border:1px solid #273957; border-radius:14px; padding:1rem 1.1rem .8rem; min-height:88px; }
    .tyres { font-size:1.22rem; font-weight:750; margin-top:.35rem; color:#edf2f7; }
    .map-note { color:#9fb0c7; font-size:.86rem; }
    </style>""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🏁 Pitwall Planner")
    st.caption("Personal Race Brief · local demo")
    st.divider()
    st.subheader("Your lineup")
    lineup = st.multiselect("Choose up to five fixture drivers", driver_names, default=driver_names[:3], max_selections=5)
    if not lineup:
        st.info("Choose a driver to build a brief.")
        st.stop()
    focus_driver = st.selectbox("Focus driver", lineup)
    focus = entries[focus_driver]
    fixture_compounds = tuple(compound.value.title() for compound in focus.available_compounds)
    st.caption(f"Fixture grid: P{focus.grid_position} · {focus.team}")
    st.caption(f"Usable fixture compounds: {' · '.join(fixture_compounds)}")
    st.divider()
    st.subheader("Race context")
    condition_label = st.radio("Race condition", ("Auto", "Dry", "Wet"), horizontal=True)
    race_condition = condition_label.lower()
    starting_compound = st.selectbox(
        "Starting tyre",
        fixture_compounds,
        help="Only compounds recorded for the selected fixture driver can be chosen.",
    )
    traffic_label = st.selectbox("Expected traffic after a stop", ("Traffic ahead", "Neutral release", "Clean air"))
    traffic_context = {"Traffic ahead": "traffic", "Neutral release": "neutral", "Clean air": "clean_air"}[traffic_label]
    degradation = st.select_slider("Tyre degradation", options=("low", "medium", "high"), value="medium")
    track_position = st.slider("Value track position", 0, 100, 55, format="%d%%")
    safety_car = st.slider("Safety Car chance", 0, 100, 35, format="%d%%")
    rain = st.slider("Rain likelihood", 0, 100, int(weekend.weather.rain_probability * 100), format="%d%%")

condition_compounds = {"dry": {"Soft", "Medium", "Hard"}, "wet": {"Intermediate", "Wet"}}
configuration_issue = (
    f"The fixture lists no {condition_label.lower()}-condition starting tyre for {focus_driver}. "
    "Choose Auto/Dry or use a fixture with recorded Intermediate or Wet tyres."
    if race_condition in condition_compounds and starting_compound not in condition_compounds[race_condition]
    else None
)
if configuration_issue:
    plans: tuple[StrategyPlan, ...] = ()
    current_snapshot: RaceScenarioSnapshot | None = None
else:
    inputs = StrategyInputs(
        degradation=degradation,
        safety_car_chance=safety_car / 100,
        rain_likelihood=rain / 100,
        pit_loss_seconds=weekend.pit_lane_loss_seconds,
        track_position_emphasis=track_position / 100,
        grid_position=focus.grid_position,
        traffic_context=traffic_context,
        race_condition=race_condition,
        starting_compound=starting_compound,
        usable_compounds=fixture_compounds,
    )
    plans = recommend_strategies(inputs)
    current_snapshot = RaceScenarioSnapshot(
        race=f"{weekend.season} {weekend.event_name}",
        lineup=tuple(lineup),
        focus_driver=focus_driver,
        inputs=inputs,
    )
team_colour = neutral_team_colour(focus.team)

with st.sidebar:
    st.divider()
    st.subheader("Scenario compare")
    if current_snapshot is None:
        st.caption("Correct the tyre/condition setup before pinning a baseline.")
    else:
        if st.button("Pin current as baseline", use_container_width=True, type="primary"):
            st.session_state["baseline_snapshot"] = current_snapshot
        st.download_button(
            "Download current scenario JSON",
            data=encode_snapshot(current_snapshot),
            file_name="pitwall-scenario.json",
            mime="application/json",
            use_container_width=True,
            help="Downloads a local deterministic snapshot. It does not create a hosted or shared link.",
        )
        if "baseline_snapshot" in st.session_state:
            st.caption("A baseline is pinned for this browser session.")

st.markdown("<div class='hero'><div class='eyebrow'>Personal race brief</div><h1>Make the call. Understand the risk.</h1><p>Compare transparent pre-race plans for your selected driver, then see exactly what would make the pitwall change its mind.</p></div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='identity'><div class='avatar' style='background:{team_colour}'>{initials(focus_driver)}</div>"
    f"<div><b>{html.escape(focus_driver)}</b><br><span class='team-token'>{html.escape(focus.team)} · fixture grid P{focus.grid_position} · identity shown as neutral product colour, not team branding</span></div></div>",
    unsafe_allow_html=True,
)

metrics = st.columns(5)
metrics[0].metric("Race distance", f"{weekend.laps} laps")
metrics[1].metric("Pit-lane loss", f"{weekend.pit_lane_loss_seconds:.1f}s")
metrics[2].metric("Air / track", f"{weekend.weather.air_temperature_c:.0f}° / {weekend.weather.track_temperature_c or '—'}°C")
metrics[3].metric("Forecast rain", f"{rain}%")
metrics[4].metric("Traffic", traffic_label)
st.caption(f"{brief.freshness.label} · {brief.freshness.detail} · As of {brief.freshness.as_of:%d %b %Y}.")

intro, read = st.columns([2, 1])
with intro:
    st.subheader(f"{weekend.event_name} · {weekend.circuit_name}")
    st.write(f"Your plan is anchored to the fixture grid and a {weekend.pit_lane_loss_seconds:.1f}s green-flag pit loss. Adjust assumptions in the sidebar to replan.")
with read:
    st.subheader("Pitwall read")
    st.write(plans[1].why_changed if plans else "A valid starting tyre and race condition are required before the strategy engine can make a call.")

st.divider()
st.subheader("Race Plan Map")
st.caption("A simplified product schematic for comparing pit timing. It is original artwork, not circuit geometry, a logo, or an official graphic.")
if configuration_issue:
    st.error(configuration_issue, icon="⛔")
    st.caption("No normal-looking plan is shown when the selected fixture cannot support the requested race condition.")
else:
    st.markdown(plan_map(plans, weekend.laps, focus_driver, focus.team), unsafe_allow_html=True)
    with st.expander("Text equivalent of the map", expanded=False):
        st.markdown("\n\n".join(f"- {plan_text(plan)}" for plan in plans))

st.divider()
st.subheader("Plan comparison")
st.caption("These are rule-based trade-offs. No plan is presented as a certainty or a win probability.")
if configuration_issue:
    st.info("Correct the race-condition or starting-tyre selection to generate a strategy comparison.")
else:
    for column, plan in zip(st.columns(3), plans):
        with column:
            plan_card(plan)

with st.expander("What changed when you moved a scenario control?", expanded=True):
    if configuration_issue:
        st.write(configuration_issue)
    else:
        st.write(plans[1].why_changed)
        st.caption("Every recommendation is recalculated from the visible fixture grid, recorded usable tyres, race condition, pit loss, weather assumption, tyre-degradation setting, traffic context, and track-position priority.")

baseline_snapshot = st.session_state.get("baseline_snapshot")
if baseline_snapshot:
    st.divider()
    st.subheader("Scenario Compare")
    st.caption("Baseline is pinned locally for this browser session. Current controls remain editable; no scenario is shared or hosted.")
    baseline_focus = baseline_snapshot.focus_driver
    baseline_inputs = baseline_snapshot.inputs
    identity, decision = st.columns([1, 2])
    with identity:
        st.markdown("**Baseline**")
        st.write(focus_driver if baseline_focus == focus_driver else baseline_focus)
        if baseline_focus != focus_driver:
            st.caption(f"Current focus: {focus_driver}")
    with decision:
        st.markdown("**Decision difference**")
        if current_snapshot is None:
            st.error("Current configuration cannot generate a valid strategy. Correct tyre/condition selection to compare calls.", icon="⛔")
        else:
            changed_inputs = input_changes(baseline_inputs, current_snapshot.inputs)
            if baseline_focus != focus_driver:
                changed_inputs.insert(0, f"**Focus driver:** {baseline_focus} → {focus_driver}")
            st.write(" · ".join(changed_inputs) if changed_inputs else "No visible assumptions changed from the baseline.")

    if current_snapshot is not None:
        with st.expander("Plan-by-plan difference", expanded=True):
            baseline_plans = recommend_strategies(baseline_inputs)
            compare_columns = st.columns(3)
            for column, baseline_plan, current_plan in zip(compare_columns, baseline_plans, plans):
                with column:
                    st.markdown(f"<div class='plan-card'><div class='eyebrow'>{html.escape(current_plan.name)}</div></div>", unsafe_allow_html=True)
                    for change in plan_changes(baseline_plan, current_plan):
                        st.caption(f"• {change}")

st.divider()
st.warning(
    "Strategy simulator — educational estimate, not official team strategy. Recommendations use public-data-oriented fixtures and scenario assumptions; live race events, tyre condition, traffic, and team information can materially change the optimal call."
)
st.caption("No driver portraits, team logos, liveries, or official F1 artwork are bundled. Optional reusable assets will require source and license attribution before use.")
