# Architecture — ServicePilot MVP

## 1. Bileşenler

```text
static/ (index.html, app.js, style.css)      Tarayıcı UI, build yok
        │  fetch /api/*
        ▼
app/main.py      FastAPI: HTTP uçları, vaka yaşam döngüsü, replay
app/store.py     SQLite (stdlib) — vaka JSON blob + ayarlar
app/jev.py       TypeSafe System One istemcisi (semantic sensor)
app/raep.py      Risk-Aware Evidence Policy — saf fonksiyonlar (Ar-Ge çekirdeği)
app/catalog.py   Uzmanlık taksonomisi, kanıt kataloğu, safety kuralları, varsayılan ayarlar
app/scenarios.py Demo / replay senaryoları (beklenen route + kanıt cevapları)
```

Jev'i başka bir typed-decision modeliyle değiştirmek = `app/jev.py`'yi değiştirmek. RAEP yalnız `signals` sözlüğünü görür (bkz. ADR-3).

## 2. Karar akışı (bir adım)

```mermaid
flowchart TD
  A[Vaka state] --> G{Safety gate}
  G -- kural eşleşti --> E1[ESCALATE]
  G -- temiz --> J[Jev tek istek: route, sufficient, critical, priority, has_*]
  J --> C{critical >= tau_crit}
  C -- evet --> E2[ESCALATE]
  C -- hayır --> R{leaf p >= tau_route ve sufficient >= tau_suff}
  R -- evet --> RT[ROUTE yaprak]
  R -- hayır --> U{max U e > 0 ve istek < limit}
  U -- evet --> REQ[REQUEST_EVIDENCE e*]
  U -- hayır --> H{p node >= tau_route olan en derin düğüm}
  H -- var --> RN[ROUTE düğüm]
  H -- yok --> E3[ESCALATE belirsiz]
```

## 3. Jev soru tasarımı (FR-3)

State (JSON): `vehicle`, `technician_note`, `dtc_codes`, `recent_repairs`, `collected_evidence[]`.

| Soru | Tip | Anlam |
|---|---|---|
| `route` | choice | Yaprak uzmanlıklar arasından sorumlu ekip; kriterler katalog açıklamaları |
| `sufficient` | noul | Toplanan bilgi, ek ölçüm/foto olmadan sorumlu uzmanlığı belirlemeye yeter mi? |
| `critical` | noul | Acil güvenlik riski (yangın/duman, fren/direksiyon kaybı, HV maruziyeti, araç sürülmemeli) |
| `priority` | score | 4 seviye: rutin → yolda kaldı/güvenlik |
| `has_<evidence>` | noul | Vaka bu kanıtın **sonucunu** zaten içeriyor mu? (serbest metinde gizli kanıtı tespit) |

Hepsi aynı state üzerinde paralel, tek round-trip. Gecikme canlı adımda ölçülür; demo gecikmeleri performans kanıtı değildir.

## 4. RAEP algoritması

Notasyon: yaprak olasılıkları `p_l` (Jev `route`), `p_crit` (Jev `critical`).

**Düğüm olasılığı:** `P(n) = Σ_{l ∈ leaves(n)} p_l`.

**Mevcut hata:** `err(s) = 1 − max_l p_l`.

**Kayıp ağırlığı:** `L(s) = 1 + w_crit · p_crit` — kritik vakada yanlış otomasyon olağan misroute'tan pahalıdır.

**Risk:** `R(s) = L(s) · err(s)`.

**Kanıt modeli (partition + reliability):** Her kanıt `e`, bir yaprak kümesi `S_e` hakkında bilgi verir ve güvenilirliği `ρ_e`'dir. Kanıt toplandığında `ρ_e` olasılıkla bilgilendiricidir: gerçek yaprağın `S_e` içinde olup olmadığı öğrenilir, içindeyse yaprak tam belirlenir. `1 − ρ_e` olasılıkla hiçbir şey değişmez.

Beklenen sonraki hata:

```
err_inf  = Σ_{l∉S_e} p_l − max_{l∉S_e} p_l
err'(e)  = ρ_e · err_inf + (1 − ρ_e) · err(s)
```

**Maliyet:** `C(e) = α·T_e + β·E_e + γ·S_e` (T: dakika, E: efor 1–5, S: güvenlik/operasyon 0–5). Katalog değerleri **uzman varsayımıdır**.

**Fayda:** `U(e) = L(s) · (err(s) − err'(e)) − λ · C(e)`.

En yüksek `U > 0` kanıt istenir. Hiçbiri pozitif değilse hiyerarşik fallback (FR-7).

**Aday filtreleri:** toplanmış kanıt; `has_<id> ≥ 0.7`; `requires_ev` ve araç elektrikli değil; `dtc_scan` ve vakada DTC var.

## 5. Baseline'lar (replay, FR-13)

| Baseline | Tanım |
|---|---|
| B — sabit checklist | Jev tek-shot'un tahmin ettiği üst grubun tüm uygulanabilir kanıtları istenir; maliyet = toplam `C(e)`; tüm cevaplarla Jev `argmax` route (eskalasyon yok) |
| C — Jev tek-shot | İlk adımda `argmax p_l`, kanıt yok, eskalasyon yok |
| ServicePilot | Jev + RAEP döngüsü |

Doğruluk: tam (yaprak eşit) ve hiyerarşik (hedef, beklenen yaprağın atası). Kritik senaryoda doğru sonuç = `ESCALATE`.

## 6. Kalıcılık

SQLite `data/servicepilot.db`: `cases(id TEXT PK, data TEXT JSON, created_at)`, `kv(key PK, value JSON)` (ayarlar). ORM yok.

## 7. Operasyonel karar izi [FR-18, FR-21]

Vaka ekranı `Jev sinyalleri → RAEP kararı → tek sıradaki işlem` ayrımını görünür tutar. Tam hesaplar, ham sinyaller, geçmiş ve araç ekleri açılır bölümlerdedir. Her karar adımı `settings` snapshot’ını ve `signal_source` bilgisini taşır. Kaynağı olmayan eski adım `unknown` kalır; `is_demo` tek başına sonraki adımların temsili olduğunu kanıtlamaz. Yeniden hesaplama kaynak/snapshot geçmişini silmez ve yeni Jev çağrısı yapmaz. Politika matematiği değişmemiştir.


## GitHub Pages + Worker sensörü [FR-22, ADR-11]
`Pages vaka metni → kimlik + origin + boyut/şema + yaklaşık oran sınırı → sabit Jev soruları → typed sinyaller → tarayıcı RAEP → yerel kayıt/insan işlemi`. Bu yol FastAPI veya SQLite'ı Worker'a taşımaz. Python `app/raep.py` ve mevcut JS politika matematiği değişmez. Worker sözleşmesi `app/jev.py` + `app/catalog.py` kaynaklarından `uv run python -m worker.export_contract` ile üretilir; drift testi vardır. Güvenlik kapısı hem istemcide hem sensörde modelden önce çalışır. Yetki/kota hatasında kanıt geçici kopyası kaydedilmez. Sağlayıcı hatası `unavailable` ile eskale edilir; fixture'a sessiz dönüş yoktur. Yeniden hesaplama kaynak etiketini ve geçmişi korur.
