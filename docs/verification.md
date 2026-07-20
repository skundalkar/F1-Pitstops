# Verification Log

## M1 initial playable brief — 2026-07-19

- Unit/integration tests: `.venv/bin/python -m pytest -q` — 6 passed.
- Syntax check: `.venv/bin/python -m py_compile app.py` — passed.
- Browser acceptance: launched local Streamlit app and verified:
  - race selector, driver lineup selector, and scenario controls render;
  - build-status dashboard is visible;
  - the lineup outlook and three strategy cards render;
  - strategy cards show tyres, pit window, risk, and a change trigger;
  - the educational-estimate warning is visible.

## Repeatable browser acceptance checklist

1. Run `.venv/bin/streamlit run app.py --server.headless true`.
2. Open `http://127.0.0.1:8501`.
3. Choose a race and up to five drivers.
4. Change rain, Safety Car, or degradation assumptions.
5. Confirm the brief and plans update, and that each plan shows its risk and
   change trigger.
6. Confirm the source/freshness statement and educational warning are present.
