# API Specification — ServicePilot MVP

Base: `http://localhost:8000`. JSON in/out. Otomatik OpenAPI: `/docs`.

## Veri modeli

### Case
```json
{
  "id": "SP-0007",
  "created_at": "2026-10-27T21:00:00Z",
  "status": "awaiting_evidence | routed | escalated",
  "scenario_id": "lv_starter | null",
  "vehicle": {"family": "Isuzu NPR 10", "fuel": "diesel | electric", "km": 184000},
  "technician_note": "Marşa basınca tık tık ses...",
  "dtc_codes": ["P0562"],
  "recent_repairs": "",
  "evidence": [{"id": "battery_voltage", "label": "Akü / şarj voltaj ölçümü", "result": "Kontak kapalı 22.8V", "at": "..."}],
  "pending_evidence": "battery_voltage | null",
  "steps": [Step],
  "final": {"action": "ROUTE", "target": "lv_electrical", "target_label": "Düşük Voltaj Elektrik"} 
}
```

### Step
```json
{
  "at": "...",
  "latency_ms": 412,
  "signals": {
    "route": {"lv_electrical": 0.91, "ecu_comm": 0.05, "...": 0.0},
    "sufficient": 0.42, "critical": 0.08,
    "priority": {"score": 2.1, "probabilities": {"0": 0.1, "1": 0.2, "2": 0.2, "3": 0.5}},
    "has": {"battery_voltage": 0.12, "...": 0.0}
  },
  "decision": {
    "action": "ROUTE | REQUEST_EVIDENCE | ESCALATE",
    "target": "lv_electrical | electrical | expert_desk | null",
    "evidence_id": "battery_voltage | null",
    "reason": "İnsan okunur gerekçe",
    "safety_hits": ["duman"],
    "risk": 0.31, "err": 0.09, "loss_weight": 1.3,
    "nodes": {"electrical": 0.96, "lv_electrical": 0.91, "...": 0.0},
    "candidates": [{"id": "battery_voltage", "label": "...", "gain": 0.07, "cost": 0.10, "U": 0.04}],
    "skipped": {"dtc_scan": "vakada DTC var"},
    "baseline_one_shot": "lv_electrical"
  }
}
```
`signals` Jev hatasında `null`; karar `ESCALATE` (NFR-8).

### Settings
```json
{"tau_route": 0.8, "tau_suff": 0.6, "tau_crit": 0.75, "lambda": 0.5,
 "alpha": 0.01, "beta": 0.05, "gamma": 0.1, "w_crit": 4.0, "max_requests": 4}
```

## Uçlar

| Metot | Yol | Gövde | Dönüş | Req |
|---|---|---|---|---|
| GET | `/api/catalog` | — | `{taxonomy, leaves, evidence, labels}` | FR-9 |
| GET | `/api/settings` | — | Settings | FR-10 |
| PUT | `/api/settings` | Settings (kısmi olabilir) | Settings | FR-10 |
| GET | `/api/cases` | — | `Case[]` (yeniden eskiye) | FR-11, FR-14 |
| POST | `/api/cases` | `{vehicle, technician_note, dtc_codes, recent_repairs, scenario_id?}` | Case (ilk adım çalışmış) | FR-1..7 |
| GET | `/api/cases/{id}` | — | Case / 404 | — |
| POST | `/api/cases/{id}/evidence` | `{evidence_id, result}` | Case (yeni adım) / 404 / 409 kapalı vaka | FR-8 |
| POST | `/api/cases/{id}/recompute` | — | Case (son adım güncel ayarlarla yeniden hesaplı) | FR-10 |
| DELETE | `/api/cases` | — | `{deleted: n}` (demo sıfırlama) | — |
| GET | `/api/scenarios` | — | `Scenario[]` | FR-12 |
| POST | `/api/replay` | — | `{settings, systems: {servicepilot, baseline_b, baseline_c}, rows: [...]}` | FR-13 |

### Scenario
```json
{"id": "lv_starter", "title": "Marş basmıyor", "vehicle": {...}, "technician_note": "...",
 "dtc_codes": [], "recent_repairs": "", "expected": "lv_electrical | ESCALATE",
 "answers": {"battery_voltage": "Kontak kapalı 21.9V, marşta 15.2V'a düşüyor"}}
```

### Replay metrikleri (sistem başına)
`n`, `exact_acc` (tam doğru / n), `hier_acc` (tam veya ata), `coverage` (otomatik ROUTE / n), `wrong_route` (yanlış otomatik ROUTE sayısı), `critical_recall`, `avg_requests`, `avg_cost`.

## Hatalar
- 404 `{"detail": "case not found"}`
- 409 `{"detail": "case closed"}` — routed/escalated vakaya kanıt eklenemez.
- 422 — doğrulama (boş not, bilinmeyen `evidence_id`).
