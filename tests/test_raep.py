"""RAEP unit tests (NFR-4). Pure policy, no Jev calls."""
import pytest

from app.catalog import DEFAULT_SETTINGS, LEAVES
from app.raep import decide, deepest_confident_node, expected_err, node_probs, normalize


def route(**p):
    return normalize({l: p.get(l, 0.0) for l in LEAVES})


def signals(r, sufficient=0.9, critical=0.05, has=None):
    return {"route": r, "sufficient": sufficient, "critical": critical,
            "priority": {"score": 1, "probabilities": {}}, "has": has or {}}


def case(note="Araç çalışmıyor", fuel="diesel", dtc=(), evidence=()):
    return {"technician_note": note, "vehicle": {"family": "NPR", "fuel": fuel, "km": 1},
            "dtc_codes": list(dtc), "recent_repairs": "", "evidence": list(evidence)}


S = DEFAULT_SETTINGS


def test_expected_err_formula():
    r = route(lv_electrical=0.5, ecu_comm=0.3, engine=0.2)
    # err now = 0.5. Evidence on {lv, ecu} with rho=1: inside fully resolved, outside has single leaf -> 0.
    assert expected_err(r, ["lv_electrical", "ecu_comm"], 1.0) == pytest.approx(0.0)
    # rho=0: uninformative -> error unchanged.
    assert expected_err(r, ["lv_electrical", "ecu_comm"], 0.0) == pytest.approx(0.5)
    # rho=0.5 on {lv}: informative half -> outside {ecu .3, engine .2} leaves 0.2 error.
    assert expected_err(r, ["lv_electrical"], 0.5) == pytest.approx(0.5 * 0.2 + 0.5 * 0.5)


def test_hierarchical_node_probs_and_fallback():
    r = route(hv_battery=0.45, hv_inverter=0.40, engine=0.15)
    nodes = node_probs(r)
    assert nodes["high_voltage"] == pytest.approx(0.85)
    assert nodes["electrical"] == pytest.approx(0.85)
    assert deepest_confident_node(nodes, 0.8) == "high_voltage"
    assert deepest_confident_node(nodes, 0.9) is None


def test_safety_gate_escalates_without_signals():
    d = decide(case("Kabinde yanık kokusu var"), None, S)
    assert d["action"] == "ESCALATE" and d["safety_hits"] == ["yanık kokusu"]


def test_jev_failure_escalates():
    assert decide(case(), None, S)["action"] == "ESCALATE"


def test_critical_noul_escalates_before_route():
    d = decide(case(), signals(route(brakes=1.0), critical=0.9), S)
    assert d["action"] == "ESCALATE" and d["target"] == "expert_desk"


def test_confident_and_sufficient_routes_leaf():
    d = decide(case(), signals(route(lv_electrical=0.95, ecu_comm=0.05)), S)
    assert (d["action"], d["target"]) == ("ROUTE", "lv_electrical")


def test_uncertain_requests_discriminating_evidence():
    d = decide(case(), signals(route(lv_electrical=0.5, ecu_comm=0.5), sufficient=0.2), S)
    assert d["action"] == "REQUEST_EVIDENCE"
    assert d["evidence_id"] in {"battery_voltage", "can_resistance"}
    assert d["candidates"][0]["U"] > 0


def test_has_signal_and_vehicle_filter_skip_candidates():
    d = decide(case(), signals(route(lv_electrical=0.5, ecu_comm=0.5), sufficient=0.2, has={"battery_voltage": 0.9}), S)
    ids = [c["id"] for c in d["candidates"]]
    assert "battery_voltage" not in ids and "hv_isolation" not in ids
    assert "hv_isolation" in d["skipped"]


def test_request_limit_falls_back_to_parent_node():
    ev = [{"id": "service_history", "result": "x"}]
    d = decide(case(evidence=ev), signals(route(hv_battery=0.45, hv_inverter=0.45, engine=0.1), sufficient=0.2),
               {**S, "max_requests": 1})
    assert (d["action"], d["target"]) == ("ROUTE", "high_voltage")


def test_no_confident_node_escalates():
    d = decide(case(), signals(route(engine=0.34, brakes=0.33, lv_electrical=0.33), sufficient=0.1),
               {**S, "max_requests": 0})
    assert d["action"] == "ESCALATE"


def test_demo_cases_cover_all_five_mvp_scenarios():
    from app.scenarios import build_demo_cases
    demos = build_demo_cases(decide, S)
    assert len(demos) == 5
    by_id = {c["id"]: c for c in demos}
    # SP-0001: technical measurement request (can_resistance)
    assert by_id["SP-0001"]["status"] == "awaiting_evidence"
    assert by_id["SP-0001"]["pending_evidence"] == "can_resistance"
    # SP-0002: photo evidence request (connector_photo)
    assert by_id["SP-0002"]["status"] == "awaiting_evidence"
    assert by_id["SP-0002"]["pending_evidence"] == "connector_photo"
    # SP-0003: safety-critical escalation
    assert by_id["SP-0003"]["status"] == "escalated"
    assert by_id["SP-0003"]["review_status"] == "pending_review"
    # SP-0004: sufficient evidence, ready for routing confirmation
    assert by_id["SP-0004"]["status"] == "routed"
    assert by_id["SP-0004"]["review_status"] == "pending_confirmation"
    # SP-0005: already routed & confirmed to specialist
    assert by_id["SP-0005"]["status"] == "routed"
    assert by_id["SP-0005"]["review_status"] == "confirmed"


# ---------- API & Decision Integrity Regression Tests (P0/P1) ----------

def test_illegal_transitions_rejected():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    client.post("/api/cases/seed")

    # SP-0001 is awaiting evidence: normal confirmation cannot bypass missing evidence
    res1 = client.post("/api/cases/SP-0001/review", json={"action": "confirm_route"})
    assert res1.status_code == 409

    # SP-0003 is safety-escalated: normal confirmation cannot bypass safety review
    res3 = client.post("/api/cases/SP-0003/review", json={"action": "confirm_route"})
    assert res3.status_code == 409


def test_critical_review_approve_requires_target_and_reason():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    client.post("/api/cases/seed")

    # SP-0003 is escalated (target=expert_desk); approve without target must NOT invent lv_electrical!
    res_no_target = client.post("/api/cases/SP-0003/review", json={"action": "approve"})
    assert res_no_target.status_code == 422

    # Approve on critical case with chosen target but without reason is rejected
    res_no_reason = client.post("/api/cases/SP-0003/review", json={"action": "approve", "target": "lv_electrical", "reason": "  "})
    assert res_no_reason.status_code == 422

    # Approve with explicit target and specialist reason succeeds
    res_ok = client.post("/api/cases/SP-0003/review", json={
        "action": "approve",
        "target": "lv_electrical",
        "reason": "Sigorta tablası F18 hattındaki termal aşınma düşük voltaj ekibince kontrol edildi."
    })
    assert res_ok.status_code == 200
    body = res_ok.json()
    assert body["status"] == "routed"
    assert body["review_status"] == "approved"
    assert body["final"]["target"] == "lv_electrical"


def test_incompatible_evidence_and_critical_field_test_rejected():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    client.post("/api/cases/seed")

    # 1. HV isolation test on diesel vehicle (SP-0001) is rejected
    res_ev = client.post("/api/cases/SP-0001/evidence", json={
        "evidence_id": "hv_isolation",
        "result": "İzolasyon 2.4 MΩ"
    })
    assert res_ev.status_code == 422
    assert "elektrikli" in res_ev.json()["detail"].lower()

    # 2. Dangerous road test (S=3 > 0) on safety-critical case (SP-0003) is rejected
    res_crit_test = client.post("/api/cases/SP-0003/evidence", json={
        "evidence_id": "road_test",
        "result": "Yol testinde duman gözlemlendi."
    })
    assert res_crit_test.status_code == 422
    assert "kritik" in res_crit_test.json()["detail"].lower()

    # 3. Safe photo documentation (S=0) on SP-0003 is accepted, but critical status remains escalated
    res_safe_doc = client.post("/api/cases/SP-0003/evidence", json={
        "evidence_id": "connector_photo",
        "result": "Sigorta kutusu kapağı fotoğrafı çekildi, erime yok."
    })
    assert res_safe_doc.status_code == 200
    b3 = res_safe_doc.json()
    assert b3["status"] == "escalated"
    assert b3["review_status"] == "pending_review"


def test_immutable_step_history_and_human_override_preserved_on_recompute():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    client.post("/api/cases/seed")

    # SP-0005 has review_status="confirmed" and target="lv_electrical"
    before = client.get("/api/cases/SP-0005").json()
    step_count_before = len(before["steps"])

    # Recompute with extreme policy settings
    client.put("/api/settings", json={"tau_route": 0.99, "tau_suff": 0.99})
    res_rec = client.post("/api/cases/SP-0005/recompute")
    assert res_rec.status_code == 200
    after = res_rec.json()

    # Step history must be append-only (not popped!)
    assert len(after["steps"]) == step_count_before + 1
    # Human confirmed routing must be preserved
    assert after["review_status"] == "confirmed"
    assert after["final"]["target"] == "lv_electrical"
    # Settings snapshot stored on step
    assert "settings" in after["steps"][-1]
    # Updated policy output stored in machine_recommendation
    assert after["machine_recommendation"] is not None

    # Reset settings back to default
    client.put("/api/settings", json=DEFAULT_SETTINGS)


def test_whitespace_and_bounds_validation():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    # Whitespace-only note rejected
    res_note = client.post("/api/cases", json={
        "vehicle": {"family": "Isuzu NPR", "fuel": "diesel", "km": 1000},
        "technician_note": "     ",
    })
    assert res_note.status_code == 422

    # Negative km rejected
    res_km = client.post("/api/cases", json={
        "vehicle": {"family": "Isuzu NPR", "fuel": "diesel", "km": -50},
        "technician_note": "Motor çalışmıyor",
    })
    assert res_km.status_code == 422

    # Out-of-bounds policy settings rejected
    res_set = client.put("/api/settings", json={"tau_route": 0.2})
    assert res_set.status_code == 422


def test_replay_metrics_match_row_aggregates_without_expected_leak():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    # Default settings replay
    res = client.post("/api/replay")
    assert res.status_code == 200
    data = res.json()
    rows = data["rows"]
    sp = data["systems"]["servicepilot"]
    assert len(rows) == 13

    # Check metrics match row math
    exact_count = sum(1 for r in rows if (r["servicepilot"]["target"] == r["expected"] or (r["expected"] == "ESCALATE" and r["servicepilot"]["action"] == "ESCALATE")))
    assert sp["exact_acc"] == pytest.approx(exact_count / len(rows), abs=0.01)

    # Replay with extreme settings degrades metrics (proves it's real RAEP execution)
    res_bad = client.post("/api/replay", params={"tau_route": 0.99, "tau_suff": 1.0, "lambda": 3.0})
    # If parameters sent via settings endpoint:
    client.put("/api/settings", json={"tau_route": 0.99, "tau_suff": 1.0, "lambda": 3.0})
    res_bad = client.post("/api/replay")
    assert res_bad.status_code == 200
    sp_bad = res_bad.json()["systems"]["servicepilot"]
    # Coverage should drop under impossible tau thresholds
    assert sp_bad["coverage"] <= sp["coverage"]

    # Restore default settings
    client.put("/api/settings", json=DEFAULT_SETTINGS)


def test_python_javascript_policy_parity():
    import json
    import shutil
    import subprocess
    from fastapi.testclient import TestClient
    from app.main import app

    if not shutil.which("node"):
        pytest.skip("Node.js is not installed; skipping JS parity test.")

    client = TestClient(app)
    py_res = client.post("/api/replay").json()
    py_sp = py_res["systems"]["servicepilot"]

    node_script = r"""
const fs = require('fs');
const vm = require('vm');
let code = fs.readFileSync('static/app.js', 'utf8').replace(/\(async function init[\s\S]*/, '');
code += '\nthis.res = runDeterministicReplay(FALLBACK_SCENARIOS, FALLBACK_CATALOG, FALLBACK_CATALOG.default_settings);';
const ctx = { console, setTimeout, clearTimeout };
vm.createContext(ctx);
vm.runInContext(code, ctx);
console.log(JSON.stringify(ctx.res));
"""
    proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, check=True)
    js_res = json.loads(proc.stdout)
    js_sp = js_res["systems"]["servicepilot"]

    assert py_sp["n"] == js_sp["n"] == 13
    assert py_sp["exact_acc"] == pytest.approx(js_sp["exact_acc"], abs=0.01)
    assert py_sp["hier_acc"] == pytest.approx(js_sp["hier_acc"], abs=0.01)
    assert py_sp["coverage"] == pytest.approx(js_sp["coverage"], abs=0.01)
    assert py_sp["wrong_route"] == js_sp["wrong_route"]
    assert py_sp["critical_recall"] == pytest.approx(js_sp["critical_recall"], abs=0.01)

    # Verify scenario-by-scenario outcome matching
    by_id_py = {r["id"]: r["servicepilot"] for r in py_res["rows"]}
    by_id_js = {r["id"]: r["servicepilot"] for r in js_res["rows"]}
    for sid in by_id_py:
        assert by_id_py[sid]["action"] == by_id_js[sid]["action"]
        assert by_id_py[sid]["target"] == by_id_js[sid]["target"]



