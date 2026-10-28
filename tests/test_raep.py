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
