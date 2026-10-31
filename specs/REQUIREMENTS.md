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
| FR-9 | Açıklanabilirlik | UI her adımda: aksiyon, gerekçe, yaprak + düğüm olasılıkları, aday kanıt tablosu, ham sinyaller, Baseline C (tek-shot) tahmini. Jev gecikmesi yalnız ölçülmüş canlı adımda gösterilir. |
| FR-10 | Politika ayarları | `GET/PUT /api/settings` ile τ_route, τ_suff, τ_crit, λ, α, β, γ, w_crit, max_requests değişir. `POST /api/cases/{id}/recompute` son Jev cevabıyla kararı Jev'i yeniden çağırmadan yeniden hesaplar. |
| FR-11 | Uzman kuyrukları | UI, ROUTE/ESCALATE edilmiş vakaları hedef ekibe göre gruplar. |
| FR-12 | Demo senaryoları | `GET /api/scenarios` hazır vakaları döner; UI tek tıkla vaka açar ve istenen kanıtın senaryo cevabını doldurabilir. |
| FR-13 | Offline replay | `POST /api/replay` tüm senaryoları senaryo cevaplarıyla otomatik koşturur ve ServicePilot / Baseline C / Baseline B metriklerini döner: routing doğruluğu (tam + hiyerarşik), otomasyon coverage, kritik recall, ortalama kanıt isteği, ortalama kanıt maliyeti. |
| FR-14 | KPI paneli | Genel bakış operasyonel durum sayılarını uygulama kayıtlarından üretir (FR-15). Doğruluk, coverage, istek ve maliyet ortalamaları ayrı sentetik replay görünümünde etiketlenir (FR-13). |
| FR-15 | Genel Bakış ekranı | Operasyonel ana ekran 4 canlı gösterge (Açık Vakalar, Kanıt Bekleyen, Uzman İncelemesinde, Yönlendirilmiş), Öncelikli Vakalar listesi ve Son Aktiviteler akışını gerçek uygulama durumundan üretir. |
| FR-16 | Vaka yönetimi ve filtreleme | Vakalar ekranı metin araması ve durum filtreleri (`Tümü`, `İnceleniyor`, `Kanıt Bekleniyor`, `Uzman Onayında`, `Yönlendirildi`) ile triyaj tablosu sunar. |
| FR-17 | Yapılandırılmış vaka ve kanıt girişi | Yeni Vaka ekranı 3 tıklanabilir adımda (`1. Araç`, `2. Şikayet`, `3. Kanıt ve Kontrol`) adım doğrulaması, sökülebilir DTC çipleri, boyut/sayı sınırlı fotoğraf önizleme, senaryo ön-doldurma ve tam taslak kaydı destekler. |
| FR-18 | Vaka detayı ve sıradaki işlem | Vaka özeti ardından tek ana işlem gösterilir: kanıt sonucu ekle, yönlendirmeyi onayla veya uzman kararı ver. Jev sinyalleri ve RAEP gerekçesi ayrı, görünür bir karar izi oluşturur. Araç detayları, görseller, tam teknik hesaplar ve append-only geçmiş açılır bölümlerde erişilebilirdir. |
| FR-19 | Uzman İncelemesi ve durum geçiş bütünlüğü | Kritik vakalar kanıt/doküman eklense dahi uzman eskalasyonunu korur ve tehlikeli saha testlerini (`S > 0`) reddeder. Kanıt bekleyen vakada normal onay verilemez; eskalasyonda hedefsiz onay reddedilir. Yeniden hesaplama (`recompute`) geçmiş adımları silmez ve insan onaylı/override edilmiş yönlendirmeyi bozmaz. |
| FR-20 | Temsili demo vakaları, dürüst replay ve mod ayrımı | İlk açılışta 5 temsili demo vakası yüklenir; yerel kayıtlarda yapılan değişiklikler yenilemede korunur. API modu ile statik yerel demo modu açıkça ayrılır; API hatasında yazma işlemi sessizce yerel moda düşmez. Statik/yerel replay, sabit sayılar veya `expected` kopyası yerine gerçek RAEP karar motorunu çalıştırır. |
| FR-21 | Anlaşılır karar izi | Genel bakış ve vaka detayında Jev’in olasılık ürettiği, RAEP’in risk/maliyet üzerinden karar verdiği ayrılır. Her adımın sinyal kaynağı açıkça etiketlenir; temsili gecikmeler canlı ölçüm gibi gösterilmez. Teknik dağılımlar, adayların fayda tablosu ve geçmiş adımlar kaybolmaz. Mobilde ana işlem teknik ayrıntılardan önce gelir. |

| FR-22 | Herkese açık canlı Jev | GitHub Pages tüm ziyaretçiler için otomatik canlı Worker sensörü kullanır; erişim kodu/giriş/istemci anahtarı yoktur. `TYPESAFE_API_KEY` yalnız Worker secret'tır ve sahibi Cloudflare panelinden değiştirir. Yeni vaka ve normal kanıt adımı canlıdır; RAEP tarayıcıda, kayıtlar cihazda kalır. Güvenlik kapısı ve yaklaşık oran sınırı korunur. Kota hatası girdiyi korur; sağlayıcı hatası `unavailable` + insan eskalasyonudur. Temsili kayıtlar ve replay canlı diye sunulmaz. |

| FR-23 | Kaydırmayla ilerleyen vaka anlatısı | Varsayılan landing page koyu, az metinli bir deneyimde tek sentetik vakayı baştan sona çözer. Lenis + GSAP ScrollTrigger ile vaka, Jev sinyalleri, RAEP kanıt seçimi, ölçüm sonucu, yeniden değerlendirme ve uzman devri görünür. Kararlar mevcut JS RAEP motoruyla hesaplanır; canlı Jev çağrısı, saha ölçümü veya arıza teşhisi gibi sunulmaz. Kritik alternatif güvenlik kapısıyla insan uzmana geçer. Çok modlu vizyon ile mevcut metin/JSON MVP ayrılır. Eski uygulama hash rotaları korunur. Landing `/ServicePilot/`, operasyonel MVP `/ServicePilot/demo/` altında sunulur; sağ üst ve kapanışta “Demoyu dene” bağlantıları bulunur. Eski `app.html` bağlantıları query/hash korunarak demoya taşınır; cihaz kayıt anahtarları değişmez. |

## Fonksiyonel olmayan gereksinimler

| ID | Gereksinim | Kabul kriteri |
|---|---|---|
| NFR-1 | Gecikme | Hedef: karar adımı p50 < 2 sn (Jev dahil); canlı ölçümle doğrulanması gerekir. |
| NFR-2 | Güvenlik | API anahtarı yalnız sunucuda; tarayıcıya veya loglara gitmez. `.env` git'e girmez. |
| NFR-3 | Kalıcılık | Vakalar SQLite'ta (`data/servicepilot.db`) saklanır; sunucu yeniden başlayınca kaybolmaz. |
| NFR-4 | Test | RAEP saf fonksiyonları (`app/raep.py`) birim testli: hiyerarşik fallback, beklenen hata formülü, safety gate, karar sırası. |
| NFR-5 | Kurulum | Tek komut: `uv run uvicorn app.main:app`; build adımı yok. |
| NFR-6 | Dil | UI Türkçe; kod/yorum İngilizce. |
| NFR-7 | Dürüstlük | Doğrulanmamış Isuzu metriği UI/spec'te gösterilmez; katalog maliyetleri "varsayım" etiketlidir. |
| NFR-8 | Dayanıklılık | Jev hatası/zaman aşımında vaka bozulmaz; adım `ESCALATE` (sebep: "Jev erişilemedi") olarak kaydedilir. |
| NFR-9 | Statik yayın | GitHub Pages yalnız `static/` dosyalarını HTTPS ile `/ServicePilot/` altında yayımlar. Anahtar, SQLite ve Python kaynakları yayın artifact'ına girmez. Statik mod canlı Jev gibi sunulmaz. `main` güncellemeleri ve manuel tetikleme aynı kontrollü workflow'u kullanır. |
| NFR-10 | Landing erişilebilirliği | Klavye ile bölüm seçimi, görünür odak, semantik anlatı, 390/768/1440px taşmasız düzen. Azaltılmış hareket veya animasyon kütüphanesi yokluğunda tüm adımlar normal belge akışında okunur. Yerel vendor dosyaları ve fontlar; build adımı gerekmez. |
| NFR-11 | Görsel proje tanıtımı | README; gerçek logo/ekran görüntüleri, rozetler, kısa açıklamalar ve oklarla sıralı karar akışı SVG’si içerir. Jev sinyali, RAEP kararı, güvenlik bypass’ı, kanıt döngüsü ve canlı/temsili ayrımı korunur. Mimari formülleri Typst kaynağından SVG olarak üretilir; mimari akışlar Mermaid kaynağıyla korunur ve SVG yeniden üretim komutları belgelenir. Kurulum ve operasyon belgelerine erişim kaybolmaz; doğrulanmamış performans/ortaklık/lisans iddiası eklenmez. |
