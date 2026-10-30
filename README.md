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

## Demo akışı (≈3 dk)

1. **Genel Bakış → Kanıt döngüsünü dene.** Gerçek bir vaka açılır. Jev olasılıkları ile RAEP kararı yan yana; tek sıradaki işlem görünür.
2. **Demo yanıtını doldur → Kanıtı ekle ve değerlendir.** CAN ölçümüyle yeterlilik değişimini ve yeni kararı görün. **Yönlendirmeyi onayla** ile ekip devrini tamamlayın.
3. Genel bakıştaki **Yönlendirme akışı** yeterli bilgi örneğini, **Güvenlik riski** Jev'den önce çalışan safety gate'i açar. Uzman kararı için ekip seçin; kritik vakada gerekçe zorunludur.
4. Vakada **Teknik karar izi**: tüm olasılıklar, ham sinyaller, aday kanıtların `U = L·Δerr − λ·C` hesabı ve adımın politika snapshot’ı. **RAEP ve replay** üzerinden ayarı değiştirip vakada yeniden hesaplayın. Yeni Jev çağrısı yapılmaz; geçmiş ve insan ataması korunur.
5. **Uzman İncelemesi → Ekip kuyrukları** ile devri, **RAEP ve replay → Simülasyonu çalıştır** ile 13 sentetik senaryonun gerçek politika sonuçlarını görün.

**Mod farkı:** FastAPI'de yeni vaka ve normal kanıt adımı canlı Jev kullanır; anahtar yoksa/hata olursa insan uzmana eskale edilir. İlk beş kayıt temsili sinyallerdir. Statik sunucu/GitHub Pages canlı Jev çağırmaz; tarayıcıdaki yerel demo motorunu kullanır. Kaynak her karar adımında etiketlidir. API yazma hatasında sessizce yerel moda geçilmez. Canlı model sonucu hazır senaryodan farklı olabilir; demo yanıtı yalnız seçilen kanıt için mevcutsa sunulur.

> Senaryolar sentetiktir; kanıt maliyetleri ve güvenilirlikleri uzman varsayımıdır. Anadolu Isuzu verisi, doğruluk veya saha tasarrufu iddiası değildir. ProEye bir devir hedefidir; canlı entegrasyon değildir.

## Doğrulama

```bash
uv run pytest -q                    # Python politika/API; her test geçici DB kullanır
node --test tests/test_frontend.mjs  # Bağımlılıksız yerel JS politika/yaşam döngüsü
node --check static/app.js
```

Gerçek Chromium akışı (Playwright yalnız test ortamına eklenir, uygulama bağımlılığı değildir):
```bash
# Terminal 1 — statik demo
python3 -m http.server 5187 --bind 127.0.0.1 --directory static
# Terminal 2
uv run --with playwright python tests/browser_smoke.py

# API arayüz testi: geçici SQLite + açıkça etiketli fixture; gerçek Jev çağrılmaz.
uv run python tests/serve_browser_fixture.py
# Ayrı terminal
uv run --with playwright python tests/browser_smoke.py --api-fixture --url http://127.0.0.1:5188
```
Chromium kurulu değilse test ortamında `uv run --with playwright playwright install chromium` gerekir. Browser testi yalnız disposable loopback sunucular içindir; fixture API'deki demo kayıtlarını sıfırlar. Canlı sunucuya karşı çalıştırmayın.

Tasarım kararları: [DESIGN.md](DESIGN.md). XERJ kurulumu, iki referans repo, sorgular ve beş skill: [referans kodlama](docs/REFERENCE_CODING.md). Kontrol kapsamı: [doğrulama kaydı](docs/VALIDATION.md).

## Yapı

```text
app/        main.py (API) · raep.py (politika) · jev.py (Jev istemcisi) · catalog.py · scenarios.py · store.py (SQLite)
static/     index.html · app.js · style.css (build yok)
specs/      PRD · REQUIREMENTS · ARCHITECTURE · API_SPEC · PLAN · DECISIONS
tests/      Python/JS regresyonları · Chromium smoke · izole API fixture
```

Geliştirme spec-driven yürür: önce `specs/`, sonra kod. Bkz. `AGENTS.md`.
