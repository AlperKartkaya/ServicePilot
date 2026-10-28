"""ServicePilot HTTP API (specs/API_SPEC.md) + static UI."""
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import jev, raep, store
from .catalog import DEFAULT_SETTINGS, EVIDENCE, LEAVES, NODES, ancestors, label, leaves_under
from .scenarios import NO_FINDING, SCENARIOS

load_dotenv()
app = FastAPI(title="ServicePilot", version="0.1.0")
client = httpx.AsyncClient()
STATUS = {"ROUTE": "routed", "ESCALATE": "escalated", "REQUEST_EVIDENCE": "awaiting_evidence"}


class Vehicle(BaseModel):
    family: str = Field(min_length=1, max_length=80)
    fuel: Literal["diesel", "electric"]
    km: int = Field(ge=0, le=5_000_000)


class CaseIn(BaseModel):
    vehicle: Vehicle
    technician_note: str = Field(min_length=3, max_length=4000)
    dtc_codes: list[str] = Field(default=[], max_length=30)
    recent_repairs: str = Field(default="", max_length=2000)
    scenario_id: str | None = None


class EvidenceIn(BaseModel):
    evidence_id: str
    result: str = Field(min_length=1, max_length=2000)


class SettingsIn(BaseModel):
    tau_route: float | None = Field(None, ge=0, le=1)
    tau_suff: float | None = Field(None, ge=0, le=1)
    tau_crit: float | None = Field(None, ge=0, le=1)
    # `lambda` is a Python keyword, hence the alias.
    lambda_: float | None = Field(None, ge=0, le=10, alias="lambda")
    alpha: float | None = Field(None, ge=0, le=1)
    beta: float | None = Field(None, ge=0, le=1)
    gamma: float | None = Field(None, ge=0, le=1)
    w_crit: float | None = Field(None, ge=0, le=20)
    max_requests: int | None = Field(None, ge=0, le=10)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_case(data: dict, cid: str):
    return {"id": cid, "created_at": now(), "status": "awaiting_evidence", "scenario_id": data.get("scenario_id"),
            "vehicle": data["vehicle"], "technician_note": data["technician_note"].strip(),
            "dtc_codes": [d.strip().upper() for d in data.get("dtc_codes", []) if d.strip()],
            "recent_repairs": data.get("recent_repairs", ""), "evidence": [], "pending_evidence": None,
            "steps": [], "final": None}


def apply(case, signals, latency_ms, s):
    d = raep.decide(case, signals, s)
    step = {"at": now(), "latency_ms": latency_ms, "signals": signals, "decision": d}
    case["steps"].append(step)
    case["status"] = STATUS[d["action"]]
    case["pending_evidence"] = d["evidence_id"]
    case["final"] = None if d["action"] == "REQUEST_EVIDENCE" else {k: d[k] for k in ("action", "target", "target_label")}
    return case


async def run_step(case, s):
    # Safety gate runs before Jev (ARCHITECTURE §2): no model call when a deterministic rule fires.
    signals, ms = (None, 0) if raep.safety_hits(case) else await jev.ask(case, client)
    return apply(case, signals, ms, s)


def load(cid):
    case = store.get_case(cid)
    if not case:
        raise HTTPException(404, "case not found")
    return case


@app.get("/api/catalog")
def catalog():
    return {"nodes": NODES, "leaves": LEAVES, "evidence": EVIDENCE, "default_settings": DEFAULT_SETTINGS}


@app.get("/api/settings")
def get_settings():
    return store.get_settings()


@app.put("/api/settings")
def put_settings(body: SettingsIn):
    return store.save_settings({**store.get_settings(), **body.model_dump(by_alias=True, exclude_none=True)})


@app.get("/api/cases")
def list_cases():
    return store.list_cases()


@app.delete("/api/cases")
def delete_cases():
    return {"deleted": store.delete_cases()}


@app.post("/api/cases")
async def create_case(body: CaseIn):
    case = await run_step(new_case(body.model_dump(), store.next_id()), store.get_settings())
    store.save_case(case)
    return case


@app.get("/api/cases/{cid}")
def get_case(cid: str):
    return load(cid)


@app.post("/api/cases/{cid}/evidence")
async def add_evidence(cid: str, body: EvidenceIn):
    case = load(cid)
    if case["status"] != "awaiting_evidence":
        raise HTTPException(409, "case closed")
    if body.evidence_id not in EVIDENCE:
        raise HTTPException(422, "unknown evidence_id")
    case["evidence"].append({"id": body.evidence_id, "label": EVIDENCE[body.evidence_id]["label"],
                             "result": body.result.strip(), "at": now()})
    case = await run_step(case, store.get_settings())
    store.save_case(case)
    return case


@app.post("/api/cases/{cid}/recompute")
def recompute(cid: str):
    """Re-run RAEP on the last stored Jev signals with current settings (ADR-7). No Jev call."""
    case = load(cid)
    last = case["steps"].pop()
    case = apply(case, last["signals"], last["latency_ms"], store.get_settings())
    case["steps"][-1]["recomputed"] = True
    store.save_case(case)
    return case


@app.get("/api/scenarios")
def scenarios():
    return SCENARIOS


# ---------- Offline replay (FR-13) ----------

def score(expected, action, target):
    exact = action == "ESCALATE" if expected == "ESCALATE" else target == expected
    hier = exact or (expected != "ESCALATE" and action == "ROUTE" and target in ancestors(expected))
    return exact, hier


def answer(sc, eid):
    return {"id": eid, "label": EVIDENCE[eid]["label"], "result": sc["answers"].get(eid, NO_FINDING), "at": now()}


async def replay_one(sc, s):
    # ServicePilot: Jev + RAEP loop with simulated technician answers.
    case = new_case(sc, sc["id"])
    while (await run_step(case, s))["status"] == "awaiting_evidence":
        case["evidence"].append(answer(sc, case["pending_evidence"]))
    sp_cost = sum(raep.evidence_cost(EVIDENCE[e["id"]], s) for e in case["evidence"])

    # Baseline C: Jev one-shot argmax on the initial state, no gate, no evidence.
    sig, _ = await jev.ask(new_case(sc, sc["id"]), client)
    c_target = max(sig["route"], key=sig["route"].get) if sig else None

    # Baseline B: fixed checklist = every applicable evidence of the one-shot top group, then Jev argmax.
    b_case = new_case(sc, sc["id"])
    b_target = None
    if c_target:
        group = (ancestors(c_target) or [c_target])[-1]
        group_leaves = set(leaves_under(group))
        b_case["evidence"] = [answer(sc, eid) for eid, ev in EVIDENCE.items()
                              if group_leaves & set(ev["informs"])
                              and not (ev.get("requires_ev") and sc["vehicle"]["fuel"] != "electric")
                              and not (eid == "dtc_scan" and sc["dtc_codes"])]
        sig_b, _ = await jev.ask(b_case, client)
        b_target = max(sig_b["route"], key=sig_b["route"].get) if sig_b else None
    b_cost = sum(raep.evidence_cost(EVIDENCE[e["id"]], s) for e in b_case["evidence"])

    f = case["final"]
    return {
        "id": sc["id"], "title": sc["title"], "expected": sc["expected"],
        "expected_label": "ESCALATE" if sc["expected"] == "ESCALATE" else label(sc["expected"]),
        "servicepilot": {"action": f["action"], "target": f["target"], "target_label": f["target_label"],
                         "requests": len(case["evidence"]), "cost": round(sp_cost, 3),
                         "evidence": [e["label"] for e in case["evidence"]],
                         "latency_ms": sum(st["latency_ms"] for st in case["steps"])},
        "baseline_b": {"action": "ROUTE" if b_target else "ESCALATE", "target": b_target,
                       "target_label": label(b_target) if b_target else None,
                       "requests": len(b_case["evidence"]), "cost": round(b_cost, 3)},
        "baseline_c": {"action": "ROUTE" if c_target else "ESCALATE", "target": c_target,
                       "target_label": label(c_target) if c_target else None, "requests": 0, "cost": 0},
    }


def metrics(rows, key):
    n = len(rows)
    crit = [r for r in rows if r["expected"] == "ESCALATE"]
    out = {"n": n, "exact": 0, "hier": 0, "routed": 0, "wrong_route": 0, "crit_hit": 0, "requests": 0, "cost": 0.0}
    for r in rows:
        x = r[key]
        exact, hier = score(r["expected"], x["action"], x["target"])
        out["exact"] += exact
        out["hier"] += hier
        out["routed"] += x["action"] == "ROUTE"
        out["wrong_route"] += x["action"] == "ROUTE" and not hier
        out["crit_hit"] += r["expected"] == "ESCALATE" and x["action"] == "ESCALATE"
        out["requests"] += x["requests"]
        out["cost"] += x["cost"]
    return {"n": n, "exact_acc": out["exact"] / n, "hier_acc": out["hier"] / n, "coverage": out["routed"] / n,
            "wrong_route": out["wrong_route"], "critical_recall": out["crit_hit"] / len(crit) if crit else None,
            "avg_requests": out["requests"] / n, "avg_cost": out["cost"] / n}


@app.post("/api/replay")
async def replay():
    s = store.get_settings()
    rows = await asyncio.gather(*(replay_one(sc, s) for sc in SCENARIOS))
    return {"settings": s, "rows": rows,
            "systems": {k: metrics(rows, k) for k in ("servicepilot", "baseline_b", "baseline_c")}}


app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent.parent / "static", html=True), name="static")
