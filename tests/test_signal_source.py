"""FR-21: model provenance must survive history/recompute without a live provider."""
import asyncio

import pytest

from app import store
from app.catalog import DEFAULT_SETTINGS


@pytest.mark.parametrize("available", [True, False])
def test_live_and_failed_signals_have_distinct_provenance(monkeypatch, available):
    from app import main
    signals = {"route": {"engine": 1.0}, "sufficient": .9, "critical": .1,
               "priority": {"score": 1}, "has": {}} if available else None

    async def ask(case, client):
        return signals, 12

    monkeypatch.setattr(main.jev, "ask", ask)
    case = main.new_case({"vehicle": {"family": "NPR", "fuel": "diesel", "km": 1},
                          "technician_note": "Motor çalışmıyor"}, "SP-0001")
    case = asyncio.run(main.run_step(case, DEFAULT_SETTINGS))
    source = "jev" if available else "unavailable"
    assert case["steps"][-1]["signal_source"] == source
    store.save_case(case)
    recomputed = main.recompute(case["id"])
    assert recomputed["steps"][-1]["signal_source"] == source
    assert recomputed["steps"][0] == case["steps"][0]


def test_safety_source_bypasses_model_and_seed_marks_fixtures(monkeypatch):
    from app import main
    async def forbidden(*args):
        raise AssertionError("Safety gate must skip Jev")

    monkeypatch.setattr(main.jev, "ask", forbidden)
    case = main.new_case({"vehicle": {"family": "NPR", "fuel": "diesel", "km": 1},
                          "technician_note": "Kabinde yanık kokusu var"}, "SP-0001")
    assert asyncio.run(main.run_step(case, DEFAULT_SETTINGS))["steps"][-1]["signal_source"] == "safety"
    seeded = main.seed_demo_data()
    assert {step["signal_source"] for case in seeded for step in case["steps"]} == {"fixture", "safety"}


def test_legacy_demo_flag_does_not_prove_a_steps_source():
    from app import main
    case = next(c for c in main.seed_demo_data() if c["id"] == "SP-0001")
    for step in case["steps"]:
        step.pop("signal_source")
    store.save_case(case)
    assert main.recompute(case["id"])["steps"][-1]["signal_source"] == "unknown"
