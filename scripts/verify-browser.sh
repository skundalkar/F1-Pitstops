#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p test-results
"$PYTHON_BIN" -m pytest -q -m e2e \
  --browser chromium \
  --screenshot only-on-failure \
  --tracing retain-on-failure \
  --output test-results

echo "Browser acceptance gate passed."
