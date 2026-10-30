"""ServicePilot HTTP API (specs/API_SPEC.md) + static UI."""
import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StrictInt, StringConstraints, field_validator

from . import jev, raep, store
from .catalog import DEFAULT_SETTINGS, ESCALATE_TARGET, EVIDENCE, LEAVES, NODES, ancestors, label, leaves_under
from .scenarios import SCENARIOS, build_demo_cases, fixture_signals_for

load_dotenv()
app = FastAPI(title="ServicePilot", version="0.1.0")
STATUS = {"ROUTE": "routed", "ESCALATE": "escalated", "REQUEST_EVIDENCE": "awaiting_evidence"}

TrimStr = Annotated[str, StringConstraints(strip_whitespace=True)]


class Vehicle(BaseModel):
    family: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=80)]
    fuel: Literal["diesel", "electric"]
    km: StrictInt = Field(ge=0, le=5_000_000)
    vin: Annotated[str, StringConstraints(strip_whitespace=True, max_length=24)] = ""
    location: Annotated[str, StringConstraints(strip_whitespace=True, max_length=120)] = ""


class AttachmentIn(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    caption: Annotated[str, StringConstraints(strip_whitespace=True, max_length=300)] = ""
    data_url: str = Field(default="", max_length=750_000)

    @field_validator("data_url")
    @classmethod
    def check_data_url(cls, v: str) -> str:
        if v and not v.startswith("data:image/"):
            raise ValueError("Yalnızca image/* veri URI formatı desteklenir.")
        return v


class CaseIn(BaseModel):
    vehicle: Vehicle
    technician_note: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=4000)]
    initial_measurements: Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)] = ""
    dtc_codes: list[str] = Field(default=[], max_length=20)
    recent_repairs: Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)] = ""
    attachments: list[AttachmentIn] = Field(default=[], max_length=4)
    scenario_id: str | None = None

    @field_validator("dtc_codes")
    @classmethod
    def clean_dtcs(cls, codes: list[str]) -> list[str]:
        out = []
        for c in codes:
            cleaned = c.strip().upper()
            if cleaned and cleaned not in out:
                if len(cleaned) > 16:
                    raise ValueError("DTC kodu en fazla 16 karakter olabilir.")
                out.append(cleaned)
        return out[:20]


class EvidenceIn(BaseModel):
    evidence_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
    result: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=2000)]
    attachment: AttachmentIn | None = None


class ReviewIn(BaseModel):
    action: Literal["confirm_route", "escalate", "approve", "override", "request_evidence"]
    target: str | None = None
    reason: Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)] = ""
    evidence_id: str | None = None


class SettingsIn(BaseModel):
    tau_route: float | None = Field(None, ge=0.5, le=0.99)
    tau_suff: float | None = Field(None, ge=0.0, le=1.0)
    tau_crit: float | None = Field(None, ge=0.1, le=0.99)
    # `lambda` is a Python keyword, hence the alias.
    lambda_: float | None = Field(None, ge=0.0, le=3.0, alias="lambda")
    alpha: float | None = Field(None, ge=0.0, le=0.05)
    beta: float | None = Field(None, ge=0.0, le=0.2)
    gamma: float | None = Field(None, ge=0.0, le=0.5)
    w_crit: float | None = Field(None, ge=0.0, le=10.0)
    max_requests: StrictInt | None = Field(None, ge=0, le=8)


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
        "machine_recommendation": None,
    }


def apply(case, signals, latency_ms, s, recomputed: bool = False, signal_source: str = "unknown"):
    ts = now()
    was_critical = raep.is_critical_case(case, s) or (
        case.get("status") == "escalated" and case.get("review_status") == "pending_review"
    )
    human_locked = case.get("review_status") in ("confirmed", "approved", "overridden") and case.get("final")

    d = raep.decide(case, signals, s)
    step = {
        "at": ts,
        "latency_ms": latency_ms,
        "signal_source": signal_source,
        "signals": signals,
        "settings": dict(s),
        "decision": d,
    }
    if recomputed:
        step["recomputed"] = True
    case["steps"].append(step)
    case["updated_at"] = ts
    case["machine_recommendation"] = {
        "action": d["action"],
        "target": d["target"],
        "target_label": d["target_label"],
        "evidence_id": d["evidence_id"],
        "reason": d["reason"],
        "at": ts,
    }

    # Preserve human-confirmed/approved/overridden assignment on recompute (P1 decision integrity).
    if recomputed and human_locked:
        rec_lbl = (
            EVIDENCE.get(d["evidence_id"], {}).get("label", d["evidence_id"])
            if d["action"] == "REQUEST_EVIDENCE"
            else d["target_label"]
        )
        case.setdefault("audit", []).append({
            "at": ts,
            "actor": "ServicePilot (RAEP)",
            "action": "Politika Yeniden Hesaplandı (İnsan Kararı Korundu)",
            "detail": f"Mevcut yönlendirme ({case['final']['target_label']}) korundu; güncel politika önerisi: {d['action']} ({rec_lbl}).",
        })
        return case

    # Preserve safety escalation if the case was already in critical escalation and unreviewed.
    if was_critical and d["action"] != "ESCALATE" and not human_locked:
        case["status"] = "escalated"
        case["review_status"] = "pending_review"
        case["final"] = {"action": "ESCALATE", "target": ESCALATE_TARGET, "target_label": label(ESCALATE_TARGET)}
        case.setdefault("audit", []).append({
            "at": ts,
            "actor": "ServicePilot (RAEP)",
            "action": "Kritik Eskalasyon Korundu",
            "detail": f"Güvenlik eskalasyonu uzman incelemesi tamamlanana kadar korundu. ({d['reason']})",
        })
        return case

    case["status"] = STATUS[d["action"]]
    case["pending_evidence"] = d["evidence_id"]
    if d["action"] == "ESCALATE":
        case["review_status"] = "pending_review"
        act_label = "Uzman İncelemesine Eskale Edildi"
    elif d["action"] == "ROUTE":
        if not human_locked:
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
    if raep.safety_hits(case):
        signals, ms, source = None, 0, "safety"
    else:
        async with httpx.AsyncClient() as http_client:
            signals, ms = await jev.ask(case, http_client)
        source = "jev" if signals is not None else "unavailable"
    return apply(case, signals, ms, s, signal_source=source)


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
    s = store.get_settings()
    if case.get("review_status") in ("confirmed", "approved", "overridden"):
        raise HTTPException(409, "case closed")
    is_crit_doc = case["status"] == "escalated" and case.get("review_status") == "pending_review"
    if case["status"] != "awaiting_evidence" and not is_crit_doc:
        raise HTTPException(409, "case closed")

    err = raep.validate_evidence_for_case(case, body.evidence_id, s)
    if err:
        raise HTTPException(422, err)

    ts = now()
    att = body.attachment.model_dump() if body.attachment else None
    if att:
        if len(case.get("attachments", [])) >= 8:
            raise HTTPException(422, "Vaka başına en fazla 8 görsel eklenebilir.")
        case.setdefault("attachments", []).append(att)

    ev_label = EVIDENCE[body.evidence_id]["label"]
    case["evidence"].append({
        "id": body.evidence_id,
        "label": ev_label,
        "result": body.result.strip(),
        "at": ts,
        "attachment": att,
    })
    case.setdefault("audit", []).append({
        "at": ts, "actor": "Teknisyen", "action": f"Kanıt Eklendi: {ev_label}", "detail": body.result.strip()
    })

    if is_crit_doc or raep.is_critical_case(case, s):
        # Critical case retains its safety escalation while attaching safe documentation.
        case["status"] = "escalated"
        case["review_status"] = "pending_review"
        if case.get("pending_evidence") == body.evidence_id:
            case["pending_evidence"] = None
        case["final"] = {"action": "ESCALATE", "target": ESCALATE_TARGET, "target_label": label(ESCALATE_TARGET)}
        case["updated_at"] = ts
        case.setdefault("audit", []).append({
            "at": ts,
            "actor": "ServicePilot (Safety Gate)",
            "action": "Doküman Eklendi · Eskalasyon Korundu",
            "detail": "Güvenlik kritik vakada eklenen bilgi uzman incelemesi için kaydedildi; otomatik yönlendirme kapalıdır.",
        })
        store.save_case(case)
        return case

    case = await run_step(case, s)
    store.save_case(case)
    return case


@app.post("/api/cases/{cid}/review")
def review_case(cid: str, body: ReviewIn):
    case = load(cid)
    s = store.get_settings()
    ts = now()
    last_dec = case["steps"][-1]["decision"] if case.get("steps") else {}
    crit = raep.is_critical_case(case, s)

    if body.action == "confirm_route":
        if case["status"] == "awaiting_evidence":
            raise HTTPException(
                409,
                "Kanıt bekleyen vakada doğrudan normal onay verilemez; önce kanıt tamamlanmalı veya gerekçeli uzman yönlendirmesi (override) yapılmalıdır.",
            )
        if case["status"] == "escalated" or crit:
            raise HTTPException(
                409,
                "Kritik veya eskale edilmiş vakada normal onay kullanılamaz; hedef ekip ve gerekçe ile uzman incelemesi gereklidir.",
            )
        proposed = last_dec.get("target") if last_dec.get("action") == "ROUTE" else (case.get("final") or {}).get("target")
        if not proposed or proposed not in NODES:
            raise HTTPException(422, "Onaylanacak geçerli bir makine yönlendirme önerisi bulunmuyor.")
        if body.target and body.target != proposed:
            raise HTTPException(422, "Önerilen ekipten farklı bir hedef seçmek için gerekçeli override aksiyonunu kullanın.")
        t_label = label(proposed)
        case["status"] = "routed"
        case["review_status"] = "confirmed"
        case["pending_evidence"] = None
        case["final"] = {"action": "ROUTE", "target": proposed, "target_label": t_label}
        case.setdefault("audit", []).append({
            "at": ts, "actor": "Servis Sorumlusu", "action": "Yönlendirme Onaylandı",
            "detail": body.reason or f"Önerilen '{t_label}' yönlendirmesi onaylanarak kaydedildi.",
        })

    elif body.action == "approve":
        if case["status"] == "awaiting_evidence":
            raise HTTPException(
                409,
                "Kanıt bekleyen vakada doğrudan onay verilemez; gerekçeli uzman override işlemi kullanılmalıdır.",
            )
        proposed = last_dec.get("target") if last_dec.get("action") == "ROUTE" and last_dec.get("target") in NODES else None
        if proposed is None:
            # Escalated / uncertain case has NO proposed specialist route; never invent lv_electrical!
            if not body.target or body.target not in NODES:
                raise HTTPException(
                    422,
                    "Eskale edilmiş vakada otomatik uzmanlık önerisi yoktur; geçerli bir hedef uzman ekip seçilmelidir.",
                )
            if crit and len(body.reason) < 3:
                raise HTTPException(422, "Kritik vaka yönlendirmesinde uzman gerekçesi (en az 3 karakter) zorunludur.")
            chosen = body.target
        else:
            if body.target and body.target != proposed:
                raise HTTPException(422, "Önerilen ekipten farklı bir hedef için override aksiyonunu kullanın.")
            chosen = proposed

        t_label = label(chosen)
        case["status"] = "routed"
        case["review_status"] = "approved"
        case["pending_evidence"] = None
        case["final"] = {"action": "ROUTE", "target": chosen, "target_label": t_label}
        case.setdefault("audit", []).append({
            "at": ts, "actor": "Merkez Uzman", "action": f"Uzman Onayı Verildi → {t_label}",
            "detail": body.reason or f"'{t_label}' uzman ekibine yönlendirme onaylandı.",
        })

    elif body.action == "override":
        if len(body.reason) < 3:
            raise HTTPException(422, "Yönlendirme değişikliği (override) için geçerli bir gerekçe zorunludur.")
        if not body.target or body.target not in NODES:
            raise HTTPException(422, "Geçerli bir hedef uzman ekip (target) seçilmelidir.")
        t_label = label(body.target)
        case["status"] = "routed"
        case["review_status"] = "overridden"
        case["pending_evidence"] = None
        case["final"] = {"action": "ROUTE", "target": body.target, "target_label": t_label}
        case.setdefault("audit", []).append({
            "at": ts, "actor": "Merkez Uzman", "action": f"Yönlendirme Değiştirildi → {t_label}",
            "detail": f"Gerekçe: {body.reason}",
        })

    elif body.action == "escalate":
        case["status"] = "escalated"
        case["review_status"] = "pending_review"
        case["pending_evidence"] = None
        case["final"] = {"action": "ESCALATE", "target": ESCALATE_TARGET, "target_label": label(ESCALATE_TARGET)}
        case.setdefault("audit", []).append({
            "at": ts, "actor": "Servis Sorumlusu", "action": "Uzman İncelemesine Alındı",
            "detail": body.reason or "Vaka uzman inceleme kuyruğuna alındı (ProEye etiketi kaydedildi).",
        })

    elif body.action == "request_evidence":
        if case.get("review_status") in ("confirmed", "approved", "overridden"):
            raise HTTPException(409, "Onaylanmış/kapatılmış vakada kanıt talebi açılamaz.")
        ev_id = (
            body.evidence_id
            or case.get("pending_evidence")
            or last_dec.get("evidence_id")
            or (last_dec.get("candidates") or [{}])[0].get("id")
        )
        if not ev_id:
            raise HTTPException(422, "İstenecek kanıt türü (evidence_id) belirtilmelidir.")
        err = raep.validate_evidence_for_case(case, ev_id, s)
        if err:
            raise HTTPException(422, err)
        ev_label = EVIDENCE[ev_id]["label"]
        case["pending_evidence"] = ev_id
        # Do NOT mutate historical step decisions, and do NOT remove critical cases from expert review!
        if crit or case["status"] == "escalated":
            case["status"] = "escalated"
            case["review_status"] = "pending_review"
            case["final"] = {"action": "ESCALATE", "target": ESCALATE_TARGET, "target_label": label(ESCALATE_TARGET)}
            case.setdefault("audit", []).append({
                "at": ts,
                "actor": "Merkez Uzman",
                "action": f"Güvenli Doküman Talebi Kaydedildi: {ev_label}",
                "detail": body.reason or f"Kritik eskalasyon korunarak '{ev_label}' bilgisi talep edildi.",
            })
        else:
            case["status"] = "awaiting_evidence"
            case["review_status"] = None
            case["final"] = None
            case.setdefault("audit", []).append({
                "at": ts,
                "actor": "Servis Sorumlusu",
                "action": f"Kanıt Talebi Kaydedildi: {ev_label}",
                "detail": body.reason or f"'{ev_label}' talebi vaka kaydına işlendi.",
            })

    case["updated_at"] = ts
    store.save_case(case)
    return case


@app.post("/api/cases/{cid}/recompute")
def recompute(cid: str):
    """Re-run RAEP on the last stored Jev signals with current settings (ADR-7). Appends step, never pops history."""
    case = load(cid)
    if not case.get("steps"):
        raise HTTPException(409, "Yeniden hesaplanacak karar adımı bulunmuyor.")
    last_with_sig = next((st for st in reversed(case["steps"]) if st.get("signals") is not None), case["steps"][-1])
    case = apply(case, last_with_sig.get("signals"), 0, store.get_settings(), recomputed=True,
                 signal_source=last_with_sig.get("signal_source", "unknown"))
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


async def replay_signals(case, sc, use_fixtures: bool):
    if raep.safety_hits(case):
        return None, 0
    if use_fixtures or not os.environ.get("TYPESAFE_API_KEY"):
        return fixture_signals_for(sc, case), 0
    async with httpx.AsyncClient() as http_client:
        return await jev.ask(case, http_client)


async def replay_one(sc, s, use_fixtures: bool = False):
    # ServicePilot: Jev + RAEP loop with scenario answers. Missing answers stay missing (never invent NO_FINDING).
    case = new_case(sc, sc["id"])
    while True:
        sig, ms = await replay_signals(case, sc, use_fixtures)
        apply(case, sig, ms, s)
        if case["status"] != "awaiting_evidence":
            break
        eid = case["pending_evidence"]
        if eid and eid in sc.get("answers", {}):
            case["evidence"].append({"id": eid, "label": EVIDENCE[eid]["label"], "result": sc["answers"][eid], "at": now()})
        else:
            # Answer not available in scenario fixture -> mark unavailable and re-evaluate without fabricating findings.
            case.setdefault("unavailable_evidence", []).append(eid)
            if len(case["unavailable_evidence"]) > len(EVIDENCE):
                break
    sp_cost = sum(raep.evidence_cost(EVIDENCE[e["id"]], s) for e in case["evidence"])

    # Baseline C: Jev one-shot argmax on the initial state, no gate, no evidence.
    init_case = new_case(sc, sc["id"])
    if use_fixtures or not os.environ.get("TYPESAFE_API_KEY"):
        sig_c = fixture_signals_for(sc, init_case)
    else:
        async with httpx.AsyncClient() as http_client:
            sig_c = (await jev.ask(init_case, http_client))[0]
    c_target = max(sig_c["route"], key=sig_c["route"].get) if sig_c else None

    # Baseline B: fixed checklist = applicable available evidence of the one-shot top group, then argmax.
    b_case = new_case(sc, sc["id"])
    b_target = None
    if c_target:
        group = (ancestors(c_target) or [c_target])[-1]
        group_leaves = set(leaves_under(group))
        b_case["evidence"] = [
            {"id": eid, "label": EVIDENCE[eid]["label"], "result": sc["answers"][eid], "at": now()}
            for eid, ev in EVIDENCE.items()
            if eid in sc.get("answers", {})
            and (group_leaves & set(ev["informs"]))
            and not (ev.get("requires_ev") and sc["vehicle"]["fuel"] != "electric")
            and not (eid == "dtc_scan" and sc["dtc_codes"])
        ]
        if use_fixtures or not os.environ.get("TYPESAFE_API_KEY"):
            sig_b = fixture_signals_for(sc, b_case)
        else:
            async with httpx.AsyncClient() as http_client:
                sig_b = (await jev.ask(b_case, http_client))[0]
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
async def replay(fixture: bool = Query(default=True)):
    s = store.get_settings()
    use_fx = fixture or not bool(os.environ.get("TYPESAFE_API_KEY"))
    rows = await asyncio.gather(*(replay_one(sc, s, use_fixtures=use_fx) for sc in SCENARIOS))
    return {
        "settings": s,
        "signal_source": "fixture" if use_fx else "live_jev",
        "rows": rows,
        "systems": {k: metrics(rows, k) for k in ("servicepilot", "baseline_b", "baseline_c")},
    }


static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/servicepilot", StaticFiles(directory=static_dir, html=True), name="static_subpath")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
