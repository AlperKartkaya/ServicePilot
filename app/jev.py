"""Jev (TypeSafe System One) client — the semantic sensor (ADR-2, ADR-3).

One request per decision step: route / sufficient / critical / priority / has_<evidence>, all in parallel.
"""
import os
import time

import httpx

from .catalog import EVIDENCE, LEAVES, NODES

URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"

PRIORITY_LEVELS = [
    "Routine: can be handled at the next planned service",
    "Vehicle works but with reduced performance or comfort",
    "Vehicle partially unusable, trips at risk",
    "Vehicle is stranded or there is a safety risk",
]


def build_state(case):
    st = {
        "vehicle": case["vehicle"],
        "technician_note": case["technician_note"],
        "dtc_codes": case.get("dtc_codes", []),
        "recent_repairs": case.get("recent_repairs", ""),
        "collected_evidence": [{"evidence": EVIDENCE[e["id"]]["desc"], "result": e["result"]} for e in case.get("evidence", [])],
    }
    if case.get("initial_measurements"):
        st["initial_measurements"] = case["initial_measurements"]
    return st


def build_questions():
    q = {
        "route": {
            "type": "choice",
            "instructions": "Which central technical support specialty is responsible for this commercial vehicle service case? "
                            "Use `technician_note`, `dtc_codes`, `vehicle`, `recent_repairs` and `collected_evidence`.",
            "criteria": {l: NODES[l]["desc"] for l in LEAVES},
        },
        "sufficient": {
            "type": "noul",
            "instructions": "Does the case already contain enough information to identify the responsible technical specialty "
                            "without asking the technician for further measurements, photos or tests?",
        },
        "critical": {
            "type": "noul",
            "instructions": "Does this service case involve an immediate safety risk for people?",
            "criteria": {
                "true": "Fire, burning smell, loss of braking or steering, high-voltage exposure, or the vehicle must not be driven.",
                "false": "No immediate danger to people; the fault affects availability, performance or comfort only.",
            },
        },
        "priority": {"type": "score", "instructions": "How urgent is this service case for the operator?", "criteria": PRIORITY_LEVELS},
    }
    for eid, ev in EVIDENCE.items():
        q[f"has_{eid}"] = {
            "type": "noul",
            "instructions": f"Does the case already contain the actual result of this check: {ev['desc']}? "
                            "Only a mention that it should be done does not count.",
        }
    return q


async def ask(case, client: httpx.AsyncClient):
    """Returns (signals, latency_ms). signals is None on any failure (NFR-8)."""
    t0 = time.perf_counter()
    try:
        r = await client.post(URL, timeout=15,
                              headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"},
                              json={"model": MODEL, "state": build_state(case), "questions": build_questions()})
        r.raise_for_status()
        a = r.json()["answers"]
        signals = {
            "route": a["route"]["probabilities"],
            "sufficient": a["sufficient"]["noul"],
            "critical": a["critical"]["noul"],
            "priority": {"score": a["priority"]["score"], "probabilities": a["priority"]["probabilities"]},
            "has": {eid: a[f"has_{eid}"]["noul"] for eid in EVIDENCE},
        }
    except (httpx.HTTPError, KeyError, ValueError) as e:
        print(f"Jev error: {type(e).__name__}: {e}")
        signals = None
    return signals, round((time.perf_counter() - t0) * 1000)
