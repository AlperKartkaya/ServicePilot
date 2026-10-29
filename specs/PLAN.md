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

## Sonraki faz (MVP dışı)
- Fotoğraf kanıtı (shadow-mode multimodal)
- Gerçek kapalı vaka verisiyle `informs`/`ρ`/maliyet kalibrasyonu
- Risk–coverage eğrisi / AURC, kalibrasyon (ECE/Brier)
- Shadow-mode log karşılaştırma (uzman ne yaptı vs ServicePilot ne önerdi)
- ProEye / DMS entegrasyonu
