"""Pitwall Planner — an explainable, local-first F1 strategy sandbox."""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st


st.set_page_config(
    page_title="Pitwall Planner",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
)


DRIVERS = {
    "Max Verstappen": {"team": "Red Bull Racing", "pace": 9.5, "reliability": 0.96, "style": "Controls tyre life from the front"},
    "Lando Norris": {"team": "McLaren", "pace": 9.1, "reliability": 0.94, "style": "Strong long-run pace"},
    "Charles Leclerc": {"team": "Ferrari", "pace": 9.0, "reliability": 0.92, "style": "High one-lap peak"},
    "Oscar Piastri": {"team": "McLaren", "pace": 8.9, "reliability": 0.94, "style": "Low-error tyre management"},
    "George Russell": {"team": "Mercedes", "pace": 8.7, "reliability": 0.93, "style": "Adaptable in mixed conditions"},
    "Lewis Hamilton": {"team": "Ferrari", "pace": 8.6, "reliability": 0.91, "style": "Patient in changing races"},
    "Kimi Antonelli": {"team": "Mercedes", "pace": 8.1, "reliability": 0.90, "style": "Upside with traffic risk"},
    "Fernando Alonso": {"team": "Aston Martin", "pace": 7.8, "reliability": 0.91, "style": "Often extracts alternate strategies"},
}

RACES = {
    "British Grand Prix · Silverstone": {
        "laps": 52,
        "pit_loss": 20.8,
        "degradation": "Medium-high",
        "overtaking": "Good",
        "default_grid": 4,
        "brief": "Fast, loaded corners make rear-tyre life and a flexible second stop decisive.",
    },
    "Italian Grand Prix · Monza": {
        "laps": 53,
        "pit_loss": 23.5,
        "degradation": "Low",
        "overtaking": "Good",
        "default_grid": 6,
        "brief": "Track position matters, but low degradation rewards extending the first stint.",
    },
    "Singapore Grand Prix · Marina Bay": {
        "laps": 62,
        "pit_loss": 28.1,
        "degradation": "High",
        "overtaking": "Difficult",
        "default_grid": 8,
        "brief": "Heat, tyre wear, traffic and Safety Car probability make contingency plans essential.",
    },
}


def strategy_cards(grid: int, rain: int, safety_car: int, degradation: int) -> list[dict[str, object]]:
    """Produce intentionally transparent heuristic recommendations for the prototype."""
    wet_risk = rain >= 35
    high_deg = degradation >= 65
    sc_likely = safety_car >= 45
    primary = "M → H" if not high_deg else "M → H → S"
    primary_window = "L18–24" if not high_deg else "L14–18, then L34–39"
    if wet_risk:
        primary = "M → H / I (weather trigger)"
        primary_window = "Protect track position; switch only when crossover is clear"
    base = 58 + (10 if grid <= 5 else 0) - (5 if grid >= 12 else 0)
    return [
        {"name": "Primary call", "tyres": primary, "window": primary_window, "chance": min(82, base + 10), "tone": "best balance", "why": "Balances tyre life with a pit window that avoids the busiest traffic."},
        {"name": "Aggressive undercut", "tyres": "S → H" if not wet_risk else "S → I", "window": "L11–15", "chance": min(72, base), "tone": "position upside", "why": "Use only if clear air is available after the stop; the new-tyre pace can unlock an undercut."},
        {"name": "Safety Car hedge", "tyres": "M → H", "window": "Wait for SC/VSC through L26" if sc_likely else "Do not wait beyond L25", "chance": min(68, base - 3 + (8 if sc_likely else 0)), "tone": "event dependent", "why": "Keeps a viable tyre set for a cheap stop if the race is neutralised."},
    ]


def driver_outlook(driver: str, grid: int, rain: int, degradation: int) -> tuple[str, str]:
    profile = DRIVERS[driver]
    modifier = (grid - 1) * 0.32 + degradation / 30 - rain / 55
    expected = max(1, min(20, round(19 - profile["pace"] * 1.45 + modifier)))
    spread = 3 + (1 if rain >= 35 else 0) + (1 if grid >= 10 else 0)
    return f"P{expected}", f"Likely range P{max(1, expected - spread)}–P{min(20, expected + spread)}"


st.markdown(
    """<style>
    .stApp { background: #0b1020; color: #edf2f7; }
    [data-testid="stSidebar"] { background: #10182b; }
    .eyebrow { color: #f5c451; font-size: .82rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .hero { padding: 1.2rem 0 .45rem; }
    .hero h1 { font-size: 2.5rem; margin: .15rem 0; }
    .hero p { color: #b7c3d3; font-size: 1.08rem; max-width: 48rem; }
    .metric-note { color: #9fb0c7; font-size: .83rem; }
    .strategy-card { background: #151f35; border: 1px solid #273957; border-radius: 14px; padding: 1rem 1.1rem; min-height: 232px; }
    .strategy-card h3 { margin: 0 0 .4rem; color: #f5c451; }
    .strategy-card .tyres { font-size: 1.3rem; font-weight: 700; margin: .5rem 0; }
    .strategy-card p { color: #bfcbdb; margin: .45rem 0; }
    </style>""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🏁 Pitwall Planner")
    st.caption("Prototype · seed context only")
    race_name = st.selectbox("Race weekend", list(RACES))
    st.divider()
    st.subheader("Your lineup")
    lineup = st.multiselect(
        "Choose up to five drivers",
        list(DRIVERS),
        default=["Lando Norris", "Charles Leclerc", "George Russell"],
        max_selections=5,
        help="This prototype uses illustrative driver profiles, not live championship data.",
    )
    grid = st.slider("Typical grid position", 1, 20, RACES[race_name]["default_grid"])
    st.divider()
    st.subheader("Race assumptions")
    rain = st.slider("Rain probability", 0, 100, 25, format="%d%%")
    safety_car = st.slider("Safety Car probability", 0, 100, 35, format="%d%%")
    degradation = st.slider("Tyre degradation", 0, 100, 55, help="0 = very low, 100 = very high")

race = RACES[race_name]
now = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
st.markdown('<div class="hero"><div class="eyebrow">Pre-race strategy brief</div><h1>Pitwall Planner</h1><p>Build a lineup, test the assumptions, and see the decision triggers—not a false promise of certainty.</p></div>', unsafe_allow_html=True)

top_left, top_mid, top_right, top_last = st.columns(4)
top_left.metric("Race distance", f"{race['laps']} laps")
top_mid.metric("Pit-lane time loss", f"{race['pit_loss']}s")
top_right.metric("Tyre wear", race["degradation"])
top_last.metric("Overtaking", race["overtaking"])
st.caption(f"Data status: illustrative seed profile · last refreshed {now} · live timing is not connected.")

brief_col, risk_col = st.columns([2, 1])
with brief_col:
    st.subheader(race_name)
    st.write(race["brief"])
with risk_col:
    st.subheader("Pitwall read")
    if rain >= 35:
        st.warning("Weather crossover is a live decision. Do not commit to intermediates from this forecast alone.")
    elif degradation >= 65:
        st.warning("High degradation: protect a second-stop option and avoid trapping the lineup in traffic.")
    else:
        st.info("Dry baseline: choose a plan with clear-air triggers rather than chasing every early stop.")

st.divider()
st.subheader("Lineup outlook")
if not lineup:
    st.info("Choose at least one driver in the sidebar to build a strategy brief.")
else:
    columns = st.columns(min(len(lineup), 5))
    for column, driver in zip(columns, lineup):
        expected, range_text = driver_outlook(driver, grid, rain, degradation)
        profile = DRIVERS[driver]
        with column:
            st.markdown(f"**{driver}**")
            st.caption(profile["team"])
            st.metric("Expected finish", expected, range_text)
            st.caption(profile["style"])

st.divider()
st.subheader("Strategy board")
st.caption("Heuristic prototype: probabilities are confidence in the plan’s suitability, not probabilities of winning.")
cards = strategy_cards(grid, rain, safety_car, degradation)
for column, card in zip(st.columns(3), cards):
    with column:
        st.markdown(
            f"<div class='strategy-card'><h3>{card['name']}</h3><span class='eyebrow'>{card['tone']}</span>"
            f"<div class='tyres'>{card['tyres']}</div><p><b>Pit window:</b> {card['window']}</p>"
            f"<p>{card['why']}</p></div>",
            unsafe_allow_html=True,
        )
        st.progress(int(card["chance"]), text=f"Plan suitability: {card['chance']}%")

with st.expander("What would change this recommendation?"):
    st.markdown(
        "- **Rain begins sooner:** keep tyre temperature and crossover evidence ahead of the forecast.\n"
        "- **Virtual/Safety Car:** recalculate pit loss before committing; a cheap stop can reverse the order.\n"
        "- **Unexpected degradation:** shorten the stint only if the new tyre will have clear air to deliver its advantage.\n"
        "- **Rival pits:** compare their out-lap pace with your traffic cost, not the pit event in isolation."
    )

st.divider()
st.caption("Pitwall Planner is an enthusiast decision-support prototype. It does not use official F1 timing, live weather, or a predictive race model yet.")
