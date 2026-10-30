"""Loopback-only API browser fixture. Temporary DB; never calls Jev or uses .env keys.
Run: uv run python tests/serve_browser_fixture.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uvicorn
from app import store

with tempfile.TemporaryDirectory(prefix="servicepilot-browser-") as directory:
    store.DB = Path(directory) / "cases.db"
    from app import main
    from app.scenarios import SCENARIOS, fixture_signals_for

    async def fixture_step(case, settings):
        scenario = next((s for s in SCENARIOS if s["id"] == case.get("scenario_id")), None)
        signals = fixture_signals_for(scenario, case) if scenario else None
        safety = bool(main.raep.safety_hits(case))
        return main.apply(case, None if safety else signals, 0, settings,
                          signal_source="safety" if safety else "fixture" if signals else "unavailable")

    main.run_step = fixture_step
    uvicorn.run(main.app, host="127.0.0.1", port=5188)
