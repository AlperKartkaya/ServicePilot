"""RAEP — Risk-Aware Evidence Policy (ARCHITECTURE §4). Pure functions, no I/O.

Input: a case dict, Jev `signals` (or None on Jev failure) and policy settings.
Output: a decision dict with action ROUTE | REQUEST_EVIDENCE | ESCALATE plus everything the UI explains.
"""
from .catalog import EVIDENCE, ESCALATE_TARGET, LEAVES, NODES, SAFETY_RULES, ancestors, label, leaves_under

HAS_THRESHOLD = 0.7  # Jev `has_<id>` above this = evidence already present in free text


def case_text(case):
    parts = [case.get("technician_note", ""), case.get("recent_repairs", ""), " ".join(case.get("dtc_codes", []))]
    parts += [e["result"] for e in case.get("evidence", [])]
    return " ".join(parts).lower()


def safety_hits(case):
    text = case_text(case)
    return [r for r in SAFETY_RULES if r in text]


def normalize(route):
    total = sum(route.get(l, 0.0) for l in LEAVES) or 1.0
    return {l: route.get(l, 0.0) / total for l in LEAVES}


def node_probs(route):
    return {n: sum(route[l] for l in leaves_under(n)) for n in NODES}


def deepest_confident_node(nodes, tau):
    ok = [n for n, p in nodes.items() if p >= tau]
    return max(ok, key=lambda n: (len(ancestors(n)), nodes[n])) if ok else None


def expected_err(route, informs, rho):
    """Partition + reliability model (ADR-4): expected 1 - max p after collecting the evidence.

    With probability rho the evidence is informative: it reveals whether the true leaf is in `informs`
    and, if so, which one. Otherwise nothing changes.
    """
    p_out = [route[l] for l in LEAVES if l not in informs]
    err_informative = sum(p_out) - max(p_out, default=0)
    return rho * err_informative + (1 - rho) * (1 - max(route.values()))


def evidence_cost(ev, s):
    return s["alpha"] * ev["T"] + s["beta"] * ev["E"] + s["gamma"] * ev["S"]


def candidates(case, signals, s, route, loss_weight, err):
    collected = {e["id"] for e in case.get("evidence", [])}
    has = signals.get("has", {})
    electric = case.get("vehicle", {}).get("fuel") == "electric"
    out, skipped = [], {}
    for eid, ev in EVIDENCE.items():
        if eid in collected:
            skipped[eid] = "toplandı"
        elif ev.get("requires_ev") and not electric:
            skipped[eid] = "araca uygun değil"
        elif eid == "dtc_scan" and case.get("dtc_codes"):
            skipped[eid] = "vakada DTC var"
        elif has.get(eid, 0) >= HAS_THRESHOLD:
            skipped[eid] = f"notta mevcut (Jev {has[eid]:.2f})"
        else:
            gain = loss_weight * (err - expected_err(route, ev["informs"], ev["rho"]))
            cost = evidence_cost(ev, s)
            out.append({"id": eid, "label": ev["label"], "gain": round(gain, 4), "cost": round(cost, 4),
                        "U": round(gain - s["lambda"] * cost, 4)})
    out.sort(key=lambda c: c["U"], reverse=True)
    return out, skipped


def decide(case, signals, s):
    d = {"action": None, "target": None, "target_label": None, "evidence_id": None, "reason": "",
         "safety_hits": safety_hits(case), "nodes": {}, "candidates": [], "skipped": {},
         "risk": None, "err": None, "loss_weight": None, "baseline_one_shot": None}

    def finish(action, reason, target=None, evidence_id=None):
        if action == "ESCALATE":
            target = ESCALATE_TARGET
        d.update(action=action, reason=reason, target=target, evidence_id=evidence_id,
                 target_label=label(target) if target else None)
        return d

    if d["safety_hits"]:
        return finish("ESCALATE", "Güvenlik kuralı tetiklendi: " + ", ".join(d["safety_hits"]))
    if signals is None:
        return finish("ESCALATE", "Jev erişilemedi; vaka insan uzmana yönlendirildi.")

    route = normalize(signals["route"])
    nodes = node_probs(route)
    best = max(route, key=route.get)
    err = 1 - route[best]
    p_crit, suff = signals["critical"], signals["sufficient"]
    L = 1 + s["w_crit"] * p_crit
    cands, skipped = candidates(case, signals, s, route, L, err)
    d.update(nodes={n: round(p, 4) for n, p in nodes.items()}, candidates=cands, skipped=skipped,
             err=round(err, 4), loss_weight=round(L, 3), risk=round(L * err, 4), baseline_one_shot=best)

    if p_crit >= s["tau_crit"]:
        return finish("ESCALATE", f"Kritik güvenlik riski olasılığı {p_crit:.2f} ≥ τ_crit {s['tau_crit']:.2f}.")
    if route[best] >= s["tau_route"] and suff >= s["tau_suff"]:
        return finish("ROUTE", f"{label(best)} olasılığı {route[best]:.2f} ve kanıt yeterliliği {suff:.2f} eşiklerin üstünde.", best)
    n_req = len(case.get("evidence", []))
    if cands and cands[0]["U"] > 0 and n_req < s["max_requests"]:
        c = cands[0]
        return finish("REQUEST_EVIDENCE", f"En yüksek net fayda: {c['label']} (U={c['U']:.3f}, risk azalması {c['gain']:.3f}, maliyet {c['cost']:.3f}).",
                      evidence_id=c["id"])
    node = deepest_confident_node(nodes, s["tau_route"])
    why = "istek limiti doldu" if n_req >= s["max_requests"] else "maliyetine değecek kanıt kalmadı"
    if node:
        kind = "yaprak uzmanlık" if node in LEAVES else "hiyerarşik fallback (üst uzmanlık)"
        return finish("ROUTE", f"{why.capitalize()}; {kind}: {label(node)} olasılığı {nodes[node]:.2f}.", node)
    return finish("ESCALATE", f"{why.capitalize()} ve hiçbir uzmanlık düğümü τ_route {s['tau_route']:.2f} eşiğine ulaşmadı.")
