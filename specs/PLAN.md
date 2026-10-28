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

## Sonraki faz (MVP dışı)
- Fotoğraf kanıtı (shadow-mode multimodal)
- Gerçek kapalı vaka verisiyle `informs`/`ρ`/maliyet kalibrasyonu
- Risk–coverage eğrisi / AURC, kalibrasyon (ECE/Brier)
- Shadow-mode log karşılaştırma (uzman ne yaptı vs ServicePilot ne önerdi)
- ProEye / DMS entegrasyonu
