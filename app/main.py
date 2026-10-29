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
from .catalog import DEFAULT_SETTINGS, ESCALATE_TARGET, EVIDENCE, LEAVES, NODES, ancestors, label, leaves_under
from .scenarios import NO_FINDING, SCENARIOS, build_demo_cases

load_dotenv()
app = FastAPI(title="ServicePilot", version="0.1.0")
client = httpx.AsyncClient()
STATUS = {"ROUTE": "routed", "ESCALATE": "escalated", "REQUEST_EVIDENCE": "awaiting_evidence"}


class Vehicle(BaseModel):
    family: str = Field(min_length=1, max_length=80)
    fuel: Literal["diesel", "electric"]
    km: int = Field(ge=0, le=5_000_000)
    vin: str = Field(default="", max_length=40)
    location: str = Field(default="", max_length=120)


class AttachmentIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    caption: str = Field(default="", max_length=300)
    data_url: str = Field(default="", max_length=2_000_000)


class CaseIn(BaseModel):
    vehicle: Vehicle
    technician_note: str = Field(min_length=3, max_length=4000)
    initial_measurements: str = Field(default="", max_length=2000)
    dtc_codes: list[str] = Field(default=[], max_length=30)
    recent_repairs: str = Field(default="", max_length=2000)
    attachments: list[AttachmentIn] = Field(default=[], max_length=10)
    scenario_id: str | None = None


class EvidenceIn(BaseModel):
    evidence_id: str
    result: str = Field(min_length=1, max_length=2000)
    attachment: AttachmentIn | None = None


class ReviewIn(BaseModel):
    action: Literal["confirm_route", "escalate", "approve", "override", "request_evidence"]
    target: str | None = None
    reason: str = Field(default="", max_length=1000)
    evidence_id: str | None = None


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
    ts = now()
    init_meas = data.get("initial_measurements", "").strip()
    loc = data.get("vehicle", {}).get("location") or "Yetkili Servis"
    return {
        "id": cid, "created_at": ts, "updated_at": ts, "status": "awaiting_evidence",
        "review_status": None, "scenario_id": data.get("scenario_id"),
        "vehicle": data["vehicle"], "technician_note": data["technician_note"].strip(),
        "initial_measurements": init_meas,
        "dtc_codes": [d.strip().upper() for d in data.get("dtc_codes", []) if d.strip()],
        "recent_repairs": data.get("recent_repairs", "").strip(),
        "attachments": data.get("attachments", []),
        "evidence": [], "pending_evidence": None, "steps": [],
        "audit": [{"at": ts, "actor": f"Teknisyen ({loc})", "action": "Vaka Oluşturuldu",
                   "detail": "Servis vakası ve başlangıç bilgileri kaydedildi."}],
        "final": None,
    }


def apply(case, signals, latency_ms, s):
    ts = now()
    d = raep.decide(case, signals, s)
    step = {"at": ts, "latency_ms": latency_ms, "signals": signals, "decision": d}
    case["steps"].append(step)
    case["updated_at"] = ts
    case["status"] = STATUS[d["action"]]
    case["pending_evidence"] = d["evidence_id"]
    if d["action"] == "ESCALATE":
        case["review_status"] = "pending_review"
        act_label = "Uzman İncelemesine Eskale Edildi"
    elif d["action"] == "ROUTE":
        if case.get("review_status") not in ("confirmed", "approved", "overridden"):
            case["review_status"] = "pending_confirmation"
        act_label = f"Yönlendirme Önerildi: {d['target_label']}"
    else:
        case["review_status"] = None
        ev_lbl = EVIDENCE.get(d["evidence_id"], {}).get("label", d["evidence_id"])
        act_label = f"Eksik Kanıt İstendi: {ev_lbl}"
    case["final"] = None if d["action"] == "REQUEST_EVIDENCE" else {k: d[k] for k in ("action", "target", "target_label")}
    case.setdefault("audit", []).append({
        "at": ts, "actor": "ServicePilot (RAEP)", "action": act_label, "detail": d["reason"]
    })
    return case


async def run_step(case, s):
    # Safety gate runs before Jev (ARCHITECTURE §2): no model call when a deterministic rule fires.
    signals, ms = (None, 0) if raep.safety_hits(case) else await jev.ask(case, client)
    return apply(case, signals, ms, s)


def seed_demo_data():
    s = store.get_settings()
    for c in build_demo_cases(raep.decide, s):
        store.save_case(c)
    return store.list_cases()


if not store.list_cases():
    seed_demo_data()


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


@app.post("/api/cases/seed")
def reset_and_seed_cases():
    store.delete_cases()
    return seed_demo_data()


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
    ts = now()
    att = body.attachment.model_dump() if body.attachment else None
    if att:
        case.setdefault("attachments", []).append(att)
    ev_label = EVIDENCE[body.evidence_id]["label"]
    case["evidence"].append({"id": body.evidence_id, "label": ev_label,
                             "result": body.result.strip(), "at": ts, "attachment": att})
    case.setdefault("audit", []).append({
        "at": ts, "actor": "Teknisyen", "action": f"Kanıt Eklendi: {ev_label}", "detail": body.result.strip()
    })
    case = await run_step(case, store.get_settings())
    store.save_case(case)
    return case


@app.post("/api/cases/{cid}/review")
def review_case(cid: str, body: ReviewIn):
    case = load(cid)
    ts = now()
    last_dec = case["steps"][-1]["decision"] if case.get("steps") else {}
    best_target = body.target or last_dec.get("target") or last_dec.get("baseline_one_shot") or "lv_electrical"
    if best_target == ESCALATE_TARGET:
        best_target = last_dec.get("baseline_one_shot") or "lv_electrical"
    if best_target not in NODES and best_target != ESCALATE_TARGET:
        raise HTTPException(422, "invalid target specialist")

    if body.action == "confirm_route":
        t_label = label(best_target)
        case["status"] = "routed"
        case["review_status"] = "confirmed"
        case["pending_evidence"] = None
        case["final"] = {"action": "ROUTE", "target": best_target, "target_label": t_label}
        case.setdefault("audit", []).append({
            "at": ts, "actor": "Servis Sorumlusu", "action": "Yönlendirme Onaylandı",
            "detail": body.reason.strip() or f"Vaka '{t_label}' uzman ekibine yönlendirildi."
        })
    elif body.action == "escalate":
        case["status"] = "escalated"
        case["review_status"] = "pending_review"
        case["pending_evidence"] = None
        case["final"] = {"action": "ESCALATE", "target": ESCALATE_TARGET, "target_label": label(ESCALATE_TARGET)}
        case.setdefault("audit", []).append({
            "at": ts, "actor": "Servis Sorumlusu", "action": "Uzman İncelemesine Gönderildi",
            "detail": body.reason.strip() or "Vaka insan uzman değerlendirmesi için ProEye masasına aktarıldı."
        })
    elif body.action == "approve":
        t_label = label(best_target)
        case["status"] = "routed"
        case["review_status"] = "approved"
        case["pending_evidence"] = None
        case["final"] = {"action": "ROUTE", "target": best_target, "target_label": t_label}
        case.setdefault("audit", []).append({
            "at": ts, "actor": "Merkez Uzman", "action": "Uzman Onayı Verildi",
            "detail": body.reason.strip() or f"Önerilen '{t_label}' yönlendirmesi uzman tarafından onaylandı."
        })
    elif body.action == "override":
        if not body.reason.strip():
            raise HTTPException(422, "override requires a reason")
        if not body.target or (body.target not in NODES and body.target != ESCALATE_TARGET):
            raise HTTPException(422, "override requires valid target")
        t_label = label(body.target)
        case["status"] = "routed"
        case["review_status"] = "overridden"
        case["pending_evidence"] = None
        case["final"] = {"action": "ROUTE", "target": body.target, "target_label": t_label}
        case.setdefault("audit", []).append({
            "at": ts, "actor": "Merkez Uzman", "action": f"Yönlendirme Değiştirildi → {t_label}",
            "detail": f"Gerekçe: {body.reason.strip()}"
        })
    elif body.action == "request_evidence":
        ev_id = body.evidence_id or last_dec.get("evidence_id") or (last_dec.get("candidates") or [{}])[0].get("id") or "connector_photo"
        if ev_id not in EVIDENCE:
            raise HTTPException(422, "unknown evidence_id")
        ev_label = EVIDENCE[ev_id]["label"]
        case["status"] = "awaiting_evidence"
        case["review_status"] = None
        case["pending_evidence"] = ev_id
        case["final"] = None
        if case.get("steps"):
            case["steps"][-1]["decision"]["action"] = "REQUEST_EVIDENCE"
            case["steps"][-1]["decision"]["evidence_id"] = ev_id
        case.setdefault("audit", []).append({
            "at": ts, "actor": "Servis Sorumlusu", "action": f"Ek Kanıt İstendi: {ev_label}",
            "detail": body.reason.strip() or f"Teknisyenden '{ev_label}' bilgisinin tamamlanması talep edildi."
        })
    case["updated_at"] = ts
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


static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/servicepilot", StaticFiles(directory=static_dir, html=True), name="static_subpath")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
