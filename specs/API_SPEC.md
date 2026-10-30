# API Specification — ServicePilot MVP

Base: `http://localhost:8000`. JSON in/out. Otomatik OpenAPI: `/docs`.

## Veri modeli

### Case
```json
{
  "id": "SP-0007",
  "created_at": "2026-10-27T21:00:00Z",
  "updated_at": "2026-10-27T21:05:00Z",
  "status": "awaiting_evidence | routed | escalated",
  "review_status": "pending_confirmation | confirmed | pending_review | approved | overridden | null",
  "scenario_id": "lv_starter | null",
  "vehicle": {"family": "Isuzu NPR 10", "fuel": "diesel | electric", "km": 184000, "vin": "NLNNPR100P0064119", "location": "Kocaeli Gebze Yetkili Servis"},
  "technician_note": "Marşa basınca tık tık ses...",
  "initial_measurements": "Akü kutup başlarında oksitlenme gözlemlendi.",
  "dtc_codes": ["P0562"],
  "recent_repairs": "",
  "attachments": [{"name": "aku-kutup-basi.jpg", "caption": "Kutup başı oksitlenme görünümü", "data_url": "data:image/svg+xml;..."}],
  "evidence": [{"id": "battery_voltage", "label": "Akü / şarj voltaj ölçümü", "result": "Kontak kapalı 22.8V", "at": "...", "attachment": null}],
  "pending_evidence": "battery_voltage | null",
  "steps": [Step],
  "audit": [{"at": "...", "actor": "Sistem (RAEP)", "action": "Kanıt İstendi", "detail": "Akü / şarj voltaj ölçümü talep edildi."}],
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
| POST | `/api/cases/{id}/evidence` | `{evidence_id, result, attachment?}` | Case (yeni adım) / 404 / 409 kapalı vaka / 422 uyumsuz kanıt | FR-8, FR-18, FR-19 |
| POST | `/api/cases/{id}/review` | `{action: "confirm_route" \| "escalate" \| "approve" \| "override" \| "request_evidence", target?, reason?, evidence_id?}` | Case / 409 geçersiz durum geçişi / 422 eksik hedef-gerekçe veya tehlikeli test | FR-18, FR-19 |
| POST | `/api/cases/{id}/recompute` | — | Case (yeni adım eklenir; insan onaylı `final` korunur, makine önerisi `machine_recommendation` alanında güncellenir) | FR-10, FR-19 |
| DELETE | `/api/cases` | — | `{deleted: n}` (demo sıfırlama ve temsili vakaları yükleme) | FR-20 |
| POST | `/api/cases/seed` | — | `Case[]` (5 temsili demo vakasını sıfırdan yükler) | FR-20 |
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

### Karar adımı kaynağı [FR-21]
`Step.signal_source`: `jev` (canlı API), `fixture` (hazır sentetik kayıt), `local` (statik demo), `safety` (Jev çağrılmadan güvenlik kuralı), `unavailable` (Jev hatası) veya `unknown` (kaynağı kaydedilmemiş eski adım). Yeniden hesaplama kaynak bilgisini devralır; yeni Jev çağrısı yapmaz. Bu alan eklemelidir; eski kayıtlara migration uygulanmaz. Temsili gecikmeler UI’da performans ölçümü olarak kullanılmaz.


## GitHub Pages Jev sensörü [FR-22, ADR-12]
Ayrı Cloudflare Worker; FastAPI uçlarını değiştirmez. Endpoint bilerek anonim kullanıma açıktır; ziyaretçi anahtarı, giriş veya erişim kodu yoktur. İzinli browser origin `https://alperkartkaya.github.io`; origin kontrolü kimlik doğrulama değildir. `TYPESAFE_API_KEY` yalnız Worker secret'tır.
- `GET /health`: `{ok:true}`; model çağrılmaz.
- `POST /infer`: `{vehicle:{family,fuel,km}, technician_note, initial_measurements?, dtc_codes?, recent_repairs?, evidence?:[{id,result}]}`. Katalog/soru/model istemciden alınmaz, VIN/konum/görseller gönderilmez. Gövde en fazla 32 KiB, alanlar mevcut vaka limitleriyle sınırlı.
- Yanıt: `{signals, latency_ms, signal_source:"jev"|"safety"|"unavailable"}`. Sinyal şekli mevcut Step sözleşmesiyle aynıdır. Güvenlik kuralı `signals:null, latency_ms:0` döner.
- `403` origin, `413` boyut, `422` şema, `429` yaklaşık ortak 5/dakika/Cloudflare-konumu limiti; istemci yazma yapmaz. `503` sağlayıcı/yanıt/eksik sunucu anahtarı hatası: `signals:null, signal_source:"unavailable"`; RAEP insan eskalasyonunu kaydeder. Hata yanıtları sağlayıcı gövdesini/anahtarı içermez. `/auth` kaldırıldı (`404`).
