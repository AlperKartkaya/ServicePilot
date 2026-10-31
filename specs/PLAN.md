# Plan — ServicePilot MVP

Durum: `[ ]` yapılacak · `[x]` bitti. Her görev gereksinim ID'si taşır.

## M0 — Spec & iskelet
- [x] AGENTS.md proje + SDD bölümü
- [x] PRD, REQUIREMENTS, ARCHITECTURE, API_SPEC, DECISIONS, PLAN
- [x] `pyproject.toml`, `.gitignore`, klasör yapısı [NFR-5, NFR-2]

## M1 — Karar çekirdeği
- [x] Katalog: taksonomi, kanıt kataloğu, safety kuralları, varsayılan ayarlar [FR-2, FR-6]
- [x] RAEP saf fonksiyonları + birim testler [FR-4..7, NFR-4]
- [x] Jev istemcisi, hata → ESCALATE [FR-3, NFR-8]

## M2 — API
- [x] SQLite store [NFR-3]
- [x] Vaka uçları: oluştur, getir, listele, kanıt ekle, recompute, sıfırla [FR-1, FR-8, FR-10]
- [x] Ayarlar uçları [FR-10]
- [x] Senaryolar + replay [FR-12, FR-13]

## M3 — UI
- [x] Yeni vaka formu + senaryo seçici [FR-1, FR-12]
- [x] Vaka detayı: karar kartı, olasılık ağacı, aday kanıt tablosu, zaman çizelgesi, kanıt girişi [FR-8, FR-9]
- [x] Uzman kuyrukları [FR-11]
- [x] KPI paneli [FR-14]
- [x] Politika ayarları [FR-10]
- [x] Replay ekranı [FR-13]

## M4 — Doğrulama
- [x] Birim testler yeşil
- [x] Tüm senaryolar uçtan uca, kritik recall %100
- [x] README: kurulum + demo akışı

## M5 — Kurumsal Koyu Tema SaaS Arayüz Yeniden Tasarımı
- [x] Tasarım dizgesi (`#090D13` / `#0E141C` / `#141C26` / `#40D9C0`) ve duyarlı uygulama kabuğu [FR-15, FR-20]
- [x] Ekran A — Genel Bakış: 4 canlı operasyonel gösterge, Öncelikli Vakalar ve Son Aktiviteler [FR-15]
- [x] Ekran B — Vakalar: arama, 5 durum filtresi ve duyarlı triyaj tablosu [FR-16]
- [x] Ekran C — Yeni Vaka: 3 bölümlü yapılandırılmış form, DTC çipleri, fotoğraf önizleme ve taslak kaydı [FR-17]
- [x] Ekran D — Vaka Detayı (%60/%40): `ServicePilot Analizi` karar paneli, `Eksik Kanıt` kartı, `Kanıt Ekle` diyaloğu ve `Karar Geçmişi` [FR-18]
- [x] Ekran E — Uzman İncelemesi: onay/override akışı, uzman kuyrukları ve RAEP politika/simülasyon görünümü [FR-19]
- [x] 5 temsili demo vakası tohumlama ve `/servicepilot/` alt yolu (GitHub Pages + FastAPI) uyumluluğu [FR-20]

## M6 — MVP Karar Bütünlüğü, Şeffaflık ve Akış Sertleştirme (P0/P1)
- [x] Geçiş kuralları: kanıt bekleyen ve kritik vakalarda doğrudan onay engellendi (409) [FR-18, FR-19]
- [x] Kritik vaka koruması: tehlikeli saha testleri (S > 0) reddedildi (422); güvenli belge/fotoğrafta eskalasyon korundu [FR-18]
- [x] Hedef doğrulaması: kritik eskalasyonda rastgele hedef uydurma engellendi; uzman hedefi ve gerekçe şartı getirildi [FR-19]
- [x] Değişmez geçmiş ve insan kararı: `recompute` append-only yapıldı; onaylı/override yönlendirmeler korundu [FR-10, FR-18]
- [x] Gerçek replay ve dürüst simülasyon: beklenen etiketten tahmin kopyalama ve sentetik "normal" bulgu uydurma kaldırıldı [FR-13]
- [x] 3 adımlı tıklanabilir sihirbaz (`Araç` → `Şikayet` → `Kanıt ve Kontrol`), taslak saklama ve dosya kotası [FR-17]
- [x] Vaka detayında üstte `Sıradaki İşlem` özeti ve mobil duyarlı sıralama [FR-18]
- [x] Tanımsız vaka (`SP-9999`) için temiz 404 / bulunamadı durumu [FR-18]
- [x] Kontrast (`--text-muted: #8E9EB2` ≥ 4.5:1), mobil çekmece odağı/Escape ve klavye erişilebilirliği [NFR-6]

## Sonraki faz (MVP dışı)
- Fotoğraf kanıtı (shadow-mode multimodal)
- Gerçek kapalı vaka verisiyle `informs`/`ρ`/maliyet kalibrasyonu
- Risk–coverage eğrisi / AURC, kalibrasyon (ECE/Brier)
- Shadow-mode log karşılaştırma (uzman ne yaptı vs ServicePilot ne önerdi)
- ProEye / DMS entegrasyonu

## M7 — Son MVP akışı [FR-9, FR-12, FR-17–21]
- [x] XERJ kurulumu, proje ve iki referans deponun yerel indeksi; beş proje-local skill
- [x] Tek işlemli vaka ekranı, görünür Jev/RAEP izi, teknik ayrıntılar için aşamalı açılım
- [x] Kısa genel bakış, üç sonuç için gerçek demo girişi ve sade form
- [x] Sinyal kaynağı, politika snapshot’ı ve geçmişin doğruluğu
- [x] JS/Python regresyonları, masaüstü/mobil tarayıcı kontrolü, demo rehberi

## M8 — GitHub Pages yayını [NFR-9, FR-20]
- [x] Yalnız statik dosyaları yayımlayan otomatik workflow
- [x] GitHub Pages etkinleştirme ve gerçek HTTPS yayın kontrolü


## M9 — Canlı Jev Worker [FR-22]
- [x] Secret, kimlik, origin, sabit soru ve limit kontrollü sensör
- [x] Pages bağlantısı, kaynak/gecikme ve hata bütünlüğü
- [x] Mock regresyonları, gerçek Worker/Jev ve Pages doğrulaması


## M10 — Herkes için kodsuz canlı yayın [FR-22, ADR-12]
- [x] Erişim kodu, token saklama, modal ve `/auth` kaldırılması; anonim regresyonlar
- [x] Worker secret korunarak public sensör ve otomatik canlı Pages yayını
- [x] Yeni anonim tarayıcı oturumunda gerçek Jev doğrulaması

## M11 — Kaydırmayla ilerleyen landing page [FR-23, NFR-7/9/10]
- [x] Yerel Lenis/GSAP, özgün koyu anlatı ve tek vakanın sayfa içinde çözülmesi
- [x] Gerçek RAEP ile sentetik sinyallerin ayrımı ve risk alternatifi
- [x] Eski uygulama rotaları, mobil/klavye/azaltılmış hareket ve regresyon doğrulaması

## M12 — Landing ve demo yayını [FR-23, NFR-9]
- [x] Sağ üst/kapanış demo bağlantıları ve `/demo/` altında mevcut MVP
- [x] Eski bağlantılar, asset yolları ve uygulama regresyonları
- [x] Commit/push, başarılı Pages workflow ve canlı iki yol doğrulaması

## M13 — Görsel README [NFR-11, FR-21/22/23]
- [x] FlightBench/izge düzeniyle logo, rozet, gerçek ekran görüntüleri ve kısa Jev açıklaması
- [x] Oklarla takip edilen SVG: safety gate, Jev, RAEP, üç aksiyon ve kanıt döngüsü
- [x] Görsel render, bağlantı/asset ve ürün gerçeği doğrulaması

## M14 — Üretilebilir mimari görselleri [NFR-11]
- [x] RAEP formüllerini Typst kaynağı ve SVG renderlarıyla sunma; politika matematiğini koruma
- [x] Mimari akışları Mermaid ile sunma; README SVG’sini olduğu gibi koruma
- [x] Render/bağlantı doğrulaması ve yalnız ilgili dokümantasyonu commit/push

## M15 — Mimari önizleme uyumluluğu [NFR-11]
- [x] Mermaid kaynaklarını ayrı dosyalarda tutup mimari belgesinde render edilmiş SVG gösterme
- [x] Kaynak/render, görsel yükleme ve README SVG’sinin değişmediğini doğrulama

## M16 — Anlaşılır diyagramlar ve yeni landing başlığı [FR-23, NFR-10/11]
M14/M15’in Mermaid sürümleri bu adımda özel SVG/PNG ile değiştirilmiştir.
- [x] Kullanıcının seçtiği başlık; mobil/masaüstü okunabilirlik ve güncel README ekran görüntüsü
- [x] Sade Türkçe özel SVG mimari diyagramları ve PNG renderları; README akışını koruma
- [x] Görsel/bağlantı, RAEP karar sırası ve landing regresyon doğrulaması

- [x] Başlık puntosunu küçültme ve README ekran görüntüsünü yeniden alma [NFR-10/11]
- [x] Başlığı hafif büyütme, satır aralığını açma ve README görselini eşitleme [NFR-10/11]

## M17 — Onaylı başlık ve dokümantasyon yayını [FR-23, NFR-9/10/11]
- [x] Son tipografi, README görseli ve mimari kaynak/render regresyon kontrolü
- [ ] İlgili değişiklikleri commit/push; başarılı Pages workflow ve canlı başlık/demo yolu doğrulaması
