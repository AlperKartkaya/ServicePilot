# Architecture Decision Records

## ADR-1 — Stack: FastAPI + SQLite + vanilla JS
- **Bağlam:** Tek kişilik, hızlı MVP; demo bir dizüstünde çalışmalı.
- **Karar:** Python/FastAPI, stdlib `sqlite3`, build adımsız statik HTML/JS/CSS.
- **Sonuç:** Kurulum tek komut. Frontend framework yok; UI büyürse (çoklu rol, gerçek zamanlı) yeniden değerlendirilir.

## ADR-2 — Jev'e HTTP ile doğrudan çağrı (SDK yok)
- **Bağlam:** System One API tek uç (`POST /v1/systemone`), JSON in/out.
- **Karar:** `httpx` ile doğrudan çağrı. Model `jev-latest`.
- **Sonuç:** Bir bağımlılık az; SDK'ya geçiş `app/jev.py` ile sınırlı.

## ADR-3 — Jev semantic sensor, RAEP karar verici
- **Bağlam:** DESCRIPTION.md: "Jev'e next_evidence nedir? diye sorup cevabını algoritma olarak sunmamalıyız."
- **Karar:** Jev yalnız olasılık üretir (`route`, `sufficient`, `critical`, `priority`, `has_*`). Sıradaki kanıt RAEP'in fayda-maliyet hesabıyla seçilir.
- **Sonuç:** Ar-Ge iddiası RAEP'te; model değiştirilebilir.

## ADR-4 — Kanıt değeri için partition + reliability modeli
- **Bağlam:** Geçmiş veri yok; gerçek `E[R(s_{t+1})|e]` öğrenilemez.
- **Karar:** Her kanıt bir yaprak kümesini ayırt eder (`informs`) ve güvenilirlik `ρ` taşır; kapalı form beklenen hata (bkz. ARCHITECTURE §4).
- **Sonuç:** Açıklanabilir, test edilebilir. PoC'de `informs`/`ρ` geçmiş vaka verisinden kalibre edilecek.

## ADR-5 — Kanıt maliyetleri varsayım
- **Bağlam:** Isuzu'ya özgü süre/efor verisi yok.
- **Karar:** Katalogda T/E/S makul uzman varsayımı; UI'da "varsayım" olarak etiketlenir. α/β/γ/λ UI'dan ayarlanabilir.

## ADR-6 — Görüntü yok
- **Bağlam:** TypeSafe image/`Box` production-ready değil.
- **Karar:** MVP text + JSON. Fotoğraf kanıtı metin açıklaması olarak girilir.

## ADR-7 — Ayar değişiminde çıkarım tekrarlanmaz
- **Bağlam:** TypeSafe rehberi: ağırlık/eşik değişimi, kanıt değişmediyse yeniden çıkarım gerektirmez.
- **Karar:** `POST /api/cases/{id}/recompute` son adımın saklı Jev sinyalleriyle RAEP'i yeniden çalıştırır.

## ADR-8 — Premium Koyu Tema Kurumsal SaaS Arayüzü ve Çift Modlu (API + Statik) Çalışma
- **Bağlam:** Arayüzün hem yerel FastAPI sunucusu (`http://localhost:8000`) hem de GitHub Pages (`/servicepilot/` alt yolu) üzerinde kusursuz çalışması ve teknisyen/uzman iş akışını 10 saniyede net biçimde aktarması gerekiyor.
- **Karar:** Vanilla HTML/CSS/JS korunarak tasarım dizgesi (`#090D13` zemin, `#0E141C` kenar çubuğu, `#141C26` kartlar, `#40D9C0` kontrollü mint vurgu, Inter + monospace tipografi) uygulandı. İstemci başlangıçta `/api/*` uçlarını kullanır; statik barındırma ortamında (ör. GitHub Pages `/servicepilot/`) API erişilemezse deterministik yerel RAEP motoru ve 5 temsili demo vakasıyla birebir aynı deneyimi sunar.
- **Sonuç:** Sıfır derleme adımı korunur, tüm mevcut testler ve API sözleşmeleri yaşar, `/servicepilot/` altında kırık varlık veya yönlendirme oluşmaz.

## ADR-9 — Tek işlemli karar masası ve görünür Jev / RAEP ayrımı [FR-18, FR-21]
- **Bağlam:** Aynı kararın sıradaki işlem, eksik kanıt, risk ve analiz kartlarında tekrarlanması akışı gizliyordu.
- **Karar:** Tek ana işlem; kısa vaka bağlamı; görünür Jev sinyalleri ve ayrı RAEP hesabı. Tam teknik iz, geçmiş ve araç bilgileri native disclosures altında. Her adım kendi politika snapshot’ını ve sinyal kaynağını taşır.
- **Sonuç:** Mevcut motor, API eylemleri ve üç adımlı form korunur. Sentetik veri veya bilinmeyen eski kaynak canlı Jev gibi sunulmaz. Mobilde ana işlem önce gelir. ADR-8’in “birebir aynı deneyim” ifadesi davranış benzerliğidir; statik mod gerçek Jev çıkarımı içermez.

## ADR-10 — Ayrı GitHub Pages yayını [NFR-9, FR-20]
- **Bağlam:** MVP paylaşılabilir bir HTTPS adresinde çalışmalı; kişisel portföy değiştirilmemeli.
- **Karar:** ServicePilot deposunda GitHub Actions ile yalnız `static/` artifact'ı yayımlanır. Python API ve anahtar GitHub Pages'e taşınmaz. Mevcut açıkça etiketli yerel demo korunur.
- **Sonuç:** Derleme veya yeni uygulama bağımlılığı gerekmez. Canlı Jev bu yayının parçası değildir; ayrıca kimlik/kullanım sınırları ve kalıcı veri tasarımı olan backend gerektirir. Sadece CORS kontrolüne güvenen herkese açık bir Jev proxy'si kurulmaz.


## ADR-11 — Kimlik kontrollü, stateless Jev Worker [FR-22, NFR-2/8/9]
- **Karar:** Pages'in mevcut yerel RAEP motoru ve tarayıcı kayıtları korunur; Worker yalnız anlamsal sensördür. Sabit soru/katalog/güvenlik kuralları Python kaynağından üretilir, serbest proxy değildir. Sunucu anahtarı Worker secret; ayrı rastgele demo kodu yalnız yetkili kullanıcının sekme oturumunda tutulur. Origin kontrolü ek katmandır, kimlik doğrulama yerine geçmez.
- **Sınırlar:** Dakikalık yerel yaklaşık oran sınırı harcama tavanı değildir. Cloudflare ücretsiz limitleri Jev fiyatlandırmasından bağımsızdır. Worker vaka veya görsel saklamaz; senkronize ekip backend'i değildir. Canlı metin TypeSafe'e gider; gerçek müşteri verisi bu demoya girilmez.


## ADR-12 — Kod istemeyen, herkese açık canlı sensör [FR-22]
- **Bağlam:** Kullanıcı, ziyaretçiden demo kodu istemeyi açıkça reddetti; kendi sunucu anahtarıyla herkesin canlı kullanmasını istedi.
- **Karar:** ADR-11'in erişim kodu ve opt-in bölümleri kaldırılır. Public Pages otomatik canlıdır; localhost statik fixture testleri yerel kalır. `/auth`, kod modalı, token saklama ve `DEMO_ACCESS_TOKEN` kaldırılır; `TYPESAFE_API_KEY` Worker secret olarak kalır.
- **Sonuç:** Origin kontrolü kimlik değildir; endpoint bilerek anonim kullanıma açıktır. Sabit sorular, boyut/şema doğrulaması, safety gate ve 5/dakika/Cloudflare-konumu yaklaşık ortak limit korunur. Bu limit katı küresel harcama tavanı değildir; sağlayıcı kredisi herkese açık kullanımla tüketilebilir.
