"""Black-box browser acceptance coverage for the Streamlit critical path.

The app is launched exactly as a customer would run it.  Keep assertions tied
to accessible labels and decision-critical content rather than Streamlit's
internal markup, which changes more frequently than the product contract.
"""

from __future__ import annotations

import os
import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Iterator

import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect


ROOT = Path(__file__).resolve().parents[1]
PORT = 8509
BASE_URL = f"http://127.0.0.1:{PORT}"


def _port_is_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        return connection.connect_ex(("127.0.0.1", port)) != 0


def _wait_for_health(url: str, timeout_seconds: int = 30) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError(f"Streamlit did not become healthy at {url}")


@pytest.fixture(scope="module")
def streamlit_url() -> Iterator[str]:
    """Start an isolated Streamlit process and retain logs for CI artifacts."""
    if not _port_is_available(PORT):
        pytest.fail(f"E2E port {PORT} is already in use; refusing to test an unknown app")

    results = ROOT / "test-results"
    results.mkdir(exist_ok=True)
    log_path = results / "streamlit-e2e.log"
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app.py",
                "--server.headless=true",
                "--server.address=127.0.0.1",
                f"--server.port={PORT}",
                "--server.fileWatcherType=none",
            ],
            cwd=ROOT,
            env={**os.environ, "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false"},
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
        try:
            _wait_for_health(f"{BASE_URL}/_stcore/health")
            yield BASE_URL
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest.mark.e2e
def test_race_brief_allows_a_user_to_replan_and_export(page, streamlit_url: str) -> None:
    """Exercise the customer-critical brief, scenario, baseline and export flow."""
    page.goto(streamlit_url, wait_until="domcontentloaded")

    expect(page.get_by_role("heading", name="Make the call. Understand the risk.")).to_be_visible(
        timeout=20_000
    )
    expect(page.locator(".plan-card").filter(has_text="Balanced")).to_be_visible()
    expect(page.get_by_text("Strategy simulator — educational estimate", exact=False)).to_be_visible()
    expect(page.get_by_text("Offline demo data", exact=False)).to_be_visible()
    expect(page.get_by_text("Illustrative fixture; no live or historical provider was queried.")).to_be_visible()

    # Pin the initial Auto scenario, then commit a material forecast change.
    # Keyboard interaction is intentional:
    # Streamlit only reruns after a real input event, while ``fill`` mutates
    # the range element without reliably committing the widget state.
    condition_group = page.get_by_role("radiogroup", name="Race condition")
    expect(condition_group.get_by_role("radio", name="Auto")).to_be_checked()
    page.get_by_role("button", name="Pin current as baseline").click()
    expect(page.get_by_role("heading", name="Scenario Compare")).to_be_visible()

    with page.expect_download() as download_info:
        page.get_by_role("button", name="Download current scenario JSON").click()
    download = download_info.value
    assert download.suggested_filename == "pitwall-scenario.json"
    exported = json.loads(download.path().read_text(encoding="utf-8"))
    assert exported["data_mode"] == "offline_seed"
    assert exported["source_label"] == "Offline demo data"
    assert "educational estimate" in exported["disclaimer"].lower()

    # The fixture does not include wet tyres. In Auto mode, an extreme forecast
    # changes the recommendation into an explicit infeasible configuration;
    # this proves the pitwall call replans rather than merely redrawing a metric.
    rain_slider = page.get_by_role("slider", name="Rain likelihood")
    # As with Streamlit's radio inputs, its visible slider track sits over the
    # native range element.  Focusing then using the keyboard is accessible
    # customer behaviour and commits a real change event.
    rain_slider.focus()
    rain_slider.press("End")
    forecast_rain = page.get_by_test_id("stMetric").filter(has_text="Forecast rain")
    expect(forecast_rain).to_contain_text("100%")
    wet_tyre_issue = page.get_by_text("requires a wet-condition starting tyre", exact=False).first
    expect(wet_tyre_issue).to_be_visible()

    # An explicit wet call with the fixture's dry-only starting tyre must not
    # render a plausible-looking recommendation. This protects a central
    # safety requirement: surface an infeasible configuration to the user.
    condition_group.get_by_text("Wet", exact=True).click()
    expect(wet_tyre_issue).to_be_visible()
