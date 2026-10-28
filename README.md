# ServicePilot — Active Evidence Orchestration (BİGGVADİ MVP)

ServicePilot, eksik bir servis vakasında **sıradaki en değerli kanıtı** seçen ve yeterli kanıt oluştuğunda vakayı doğru uzmanlığa yönlendiren karar katmanıdır. Arıza teşhisi yapmaz.

- **Jev (TypeSafe System One)** → anlamsal sensör: tek istekte route/sufficient/critical/priority/has_* olasılıkları.
- **RAEP (Risk-Aware Evidence Policy)** → `app/raep.py`: safety gate, hiyerarşik routing, kanıt fayda-maliyet hesabı, eskalasyon.
- Aksiyonlar: `ROUTE` · `REQUEST_EVIDENCE` · `ESCALATE`.

## Kurulum

```bash
# .env içinde: TYPESAFE_API_KEY=...
uv sync
uv run uvicorn app.main:app --reload
# http://localhost:8000      UI
# http://localhost:8000/docs OpenAPI
uv run pytest -q             # RAEP birim testleri
```

## Demo akışı (≈5 dk)

1. **Yeni Vaka → Demo senaryoları** → "Seyirde ara ara stop etme (belirsiz)". RAEP kanıt ister; aday kanıt tablosunda U = L·Δerr − λ·C değerleri görünür.
2. **Senaryo cevabını doldur → Kanıtı gönder**. Her adımda Jev yeniden çağrılır; zaman çizelgesi büyür, sonunda ROUTE.
3. "Torpido arkasından yanık kokusu" → safety gate, Jev çağrılmadan ESCALATE. "Fren pedalı derine gidiyor" → Jev `critical` ile ESCALATE.
4. **Politika Ayarları** → λ'yı düşür / τ_route'u yükselt → vakada "Güncel ayarlarla yeniden hesapla" (Jev çağrısız).
5. **Uzman Kuyrukları** → vakalar ekip ve ProEye masasına göre.
6. **Değerlendirme → Replay çalıştır** → ServicePilot vs Baseline B (sabit checklist) vs Baseline C (Jev tek-shot).

> Senaryolar sentetiktir; kanıt maliyetleri ve güvenilirlikleri uzman varsayımıdır. Anadolu Isuzu verisi veya doğruluk iddiası değildir.

## Yapı

```text
app/        main.py (API) · raep.py (politika) · jev.py (Jev istemcisi) · catalog.py · scenarios.py · store.py (SQLite)
static/     index.html · app.js · style.css (build yok)
specs/      PRD · REQUIREMENTS · ARCHITECTURE · API_SPEC · PLAN · DECISIONS
tests/      test_raep.py
```

Geliştirme spec-driven yürür: önce `specs/`, sonra kod. Bkz. `AGENTS.md`.
