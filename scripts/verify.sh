#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

"$PYTHON_BIN" -m ruff check .
"$PYTHON_BIN" -m pytest -q -m "not e2e" \
  --cov=pitwall --cov=data_sources --cov-branch --cov-report=term-missing \
  --cov-fail-under=80
"$PYTHON_BIN" -m py_compile app.py

if [[ -n "${CI_DIFF_BASE:-}" && "${CI_DIFF_BASE}" != "0000000000000000000000000000000000000000" ]]; then
  git diff --check "${CI_DIFF_BASE}...HEAD"
else
  git diff --check
fi

echo "Unit quality gate passed. Run ./scripts/verify-browser.sh when Playwright Chromium is installed."
