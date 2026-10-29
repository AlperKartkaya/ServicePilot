# Requirements Specification — ServicePilot MVP

Her gereksinim bir kabul kriteri (AC) taşır. Kod değişiklikleri bu ID'lere referans verir.

## Fonksiyonel gereksinimler

| ID | Gereksinim | Kabul kriteri |
|---|---|---|
| FR-1 | Vaka oluşturma | `POST /api/cases` araç, not, DTC, son onarımlar alanlarıyla vaka açar; not boşsa 422 döner. |
| FR-2 | Safety gate | Not/DTC/kanıtta kritik anahtar kelime (ör. "duman", "yangın", "fren tutmuyor", "izolasyon hatası") varsa Jev sonucundan bağımsız `ESCALATE` verilir ve tetikleyen kural gösterilir. |
| FR-3 | Jev sinyalleri | Her karar adımında **tek** Jev isteği atılır: `route` (choice, yaprak uzmanlıklar), `sufficient`, `critical` (noul), `priority` (score), her aday kanıt için `has_<id>` (noul). Ham cevaplar adımda saklanır. |
| FR-4 | Kritik eskalasyon | `critical ≥ τ_crit` ise `ESCALATE`. |
| FR-5 | Doğrudan routing | En olası yaprak `p ≥ τ_route` ve `sufficient ≥ τ_suff` ise `ROUTE` (yaprak). |
| FR-6 | Kanıt isteme | Aksi halde en yüksek `U(e) > 0` olan kanıt `REQUEST_EVIDENCE` olarak istenir; tüm adayların `gain`, `cost`, `U` değerleri gösterilir. Toplanmış, notta zaten bulunan (`has_<id> ≥ 0.7`) veya araca uygun olmayan (ör. dizelde HV) kanıt aday olmaz. |
| FR-7 | Hiyerarşik fallback | Faydalı kanıt kalmadıysa veya istek limiti dolduysa `p ≥ τ_route` olan **en derin** taksonomi düğümüne `ROUTE`; yoksa `ESCALATE` (belirsiz). |
| FR-8 | Kanıt girişi | `POST /api/cases/{id}/evidence` kanıt sonucunu ekler ve yeni karar adımı üretir. Yalnız açık vakalarda çalışır. |
| FR-9 | Açıklanabilirlik | UI her adımda: aksiyon, gerekçe, yaprak + düğüm olasılıkları, aday kanıt tablosu, Jev gecikmesi, Baseline C (tek-shot) tahmini. |
| FR-10 | Politika ayarları | `GET/PUT /api/settings` ile τ_route, τ_suff, τ_crit, λ, α, β, γ, w_crit, max_requests değişir. `POST /api/cases/{id}/recompute` son Jev cevabıyla kararı Jev'i yeniden çağırmadan yeniden hesaplar. |
| FR-11 | Uzman kuyrukları | UI, ROUTE/ESCALATE edilmiş vakaları hedef ekibe göre gruplar. |
| FR-12 | Demo senaryoları | `GET /api/scenarios` hazır vakaları döner; UI tek tıkla vaka açar ve istenen kanıtın senaryo cevabını doldurabilir. |
| FR-13 | Offline replay | `POST /api/replay` tüm senaryoları senaryo cevaplarıyla otomatik koşturur ve ServicePilot / Baseline C / Baseline B metriklerini döner: routing doğruluğu (tam + hiyerarşik), otomasyon coverage, kritik recall, ortalama kanıt isteği, ortalama kanıt maliyeti. |
| FR-14 | KPI paneli | UI vaka sayısı, otomatik route oranı, eskalasyon oranı, ortalama kanıt isteği, ortalama Jev gecikmesi gösterir. |
| FR-15 | Genel Bakış ekranı | Operasyonel ana ekran 4 canlı gösterge (Açık Vakalar, Kanıt Bekleyen, Uzman İncelemesinde, Yönlendirilmiş), Öncelikli Vakalar listesi ve Son Aktiviteler akışını gerçek uygulama durumundan üretir. |
| FR-16 | Vaka yönetimi ve filtreleme | Vakalar ekranı metin araması ve durum filtreleri (`Tümü`, `İnceleniyor`, `Kanıt Bekleniyor`, `Uzman Onayında`, `Yönlendirildi`) ile triyaj tablosu sunar. |
| FR-17 | Yapılandırılmış vaka ve kanıt girişi | Yeni Vaka ekranı 3 bölümde (Araç Bilgileri, Arıza Açıklaması + sökülebilir DTC çipleri, Kanıtlar + fotoğraf önizleme ve ilk ölçümler) doğrulama ve taslak kaydı destekler. |
| FR-18 | İki sütunlu Vaka Detayı ve Karar Paneli | Sol sütun (%60) vaka özeti, DTC, görseller, geçmiş ve kanıt zaman çizelgesini; sağ sütun (%40) `ServicePilot Analizi` altında önerilen ekip, gerekçe, öncelikli `Eksik Kanıt` kartı (`Kanıt Ekle` aksiyonlu), `Risk ve İnsan Onayı`, duruma bağlı aksiyonlar ve `Karar Geçmişi` denetim izini gösterir. |
| FR-19 | Uzman İncelemesi ve onay/override | Uzman İncelemesi ekranı eskalasyon nedenini, kritiklik seviyesini ve kanıtları sunar; uzmanın önerilen ekibi onaylamasını veya gerekçe yazarak farklı uzman ekibe yönlendirmesini (`override`) kayıt altına alır. |
| FR-20 | Temsili demo vakaları ve statik uyumluluk | Sistem ilk açılışta veya sıfırlamada 5 temsili demo vakasını (`Demo Ortamı` etiketli) hazırlar; `/servicepilot/` alt yolu (GitHub Pages) ve yerel FastAPI sunucusu altında eksiksiz çalışır. |

## Fonksiyonel olmayan gereksinimler

| ID | Gereksinim | Kabul kriteri |
|---|---|---|
| NFR-1 | Gecikme | Karar adımı p50 < 2 sn (Jev dahil). |
| NFR-2 | Güvenlik | API anahtarı yalnız sunucuda; tarayıcıya veya loglara gitmez. `.env` git'e girmez. |
| NFR-3 | Kalıcılık | Vakalar SQLite'ta (`data/servicepilot.db`) saklanır; sunucu yeniden başlayınca kaybolmaz. |
| NFR-4 | Test | RAEP saf fonksiyonları (`app/raep.py`) birim testli: hiyerarşik fallback, beklenen hata formülü, safety gate, karar sırası. |
| NFR-5 | Kurulum | Tek komut: `uv run uvicorn app.main:app`; build adımı yok. |
| NFR-6 | Dil | UI Türkçe; kod/yorum İngilizce. |
| NFR-7 | Dürüstlük | Doğrulanmamış Isuzu metriği UI/spec'te gösterilmez; katalog maliyetleri "varsayım" etiketlidir. |
| NFR-8 | Dayanıklılık | Jev hatası/zaman aşımında vaka bozulmaz; adım `ESCALATE` (sebep: "Jev erişilemedi") olarak kaydedilir. |
