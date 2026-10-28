# PRD — ServicePilot MVP

**Durum:** v0.1 (BİGGVADİ demo MVP) · **Kaynak:** `DESCRIPTION.md` · **Tarih:** 2026-10-27

## 1. Problem

Dağıtık ticari araç servis ağlarında merkez teknik uzmanlar, eksik veya heterojen kanıtla gelen vakaları değerlendirmek ve eksik kanıtı tekrar istemek zorunda kalabilir. Bu, uzman dakikasını ve vaka çözüm süresini artırır.

> Not: Anadolu Isuzu'ya özgü dakika/maliyet verisi **yoktur**. MVP bu değerleri ölçmek için altyapı sunar; uydurulmuş sayı kullanmaz.

## 2. Ürün tanımı

ServicePilot, servis problemini teşhis eden bir AI **değildir**. Her vaka için:

- **ROUTE** — vakayı doğru uzman ekibe yönlendirir (emin değilse bir üst uzmanlık seviyesine: hiyerarşik fallback),
- **REQUEST_EVIDENCE** — karar riskini en çok düşüren ve maliyeti en düşük **sıradaki kanıtı** ister,
- **ESCALATE** — güvenlik riski veya çözülemeyen belirsizlikte insan uzmana (ProEye / Expert Desk) eskale eder.

Jev (TypeSafe) anlamsal sensördür; kararı **RAEP** (Risk-Aware Evidence Policy) verir.

## 3. Kullanıcılar

| Persona | İhtiyaç |
|---|---|
| Servis teknisyeni | Vakayı hızlı açmak, ne ölçmesi/çekmesi gerektiğini net görmek |
| Merkez teknik uzman | Önüne hazırlanmış, doğru kuyruğa düşmüş vaka |
| Teknik destek yöneticisi | KPI, politika ayarları (eşikler, maliyet ağırlıkları) |
| BİGG jürisi (demo) | Kararın açıklanabilirliği, baseline karşılaştırması, risk-coverage |

## 4. MVP kapsamı (In)

1. Vaka açma formu: araç ailesi, yakıt tipi, km, DTC, teknisyen notu, son onarımlar.
2. Deterministik safety gate (anahtar kelime kuralları).
3. Jev tek çağrıda paralel sorular: route `choice`, `sufficient` / `critical` `noul`, `priority` `score`, aday kanıt varlık `noul`'ları.
4. RAEP: hiyerarşik routing, kanıt değer/maliyet hesabı, eskalasyon.
5. Kanıt döngüsü: teknisyen istenen kanıtı girer → yeniden karar.
6. Açıklanabilir UI: olasılık ağacı, aday kanıt tablosu (fayda/maliyet/U), adım zaman çizelgesi, baseline (Jev tek-shot) karşılaştırması.
7. Uzman kuyrukları görünümü.
8. Politika ayarları UI (eşikler, λ, α/β/γ, kritik ağırlık) — çıkarımı tekrarlamadan kararı yeniden hesaplar.
9. Demo senaryoları + offline replay değerlendirmesi (baseline'lara karşı metrikler).

## 5. Kapsam dışı (Out)

- Fotoğraf/görüntü ve `Box` (TypeSafe deneysel) — sonraki faz, shadow-mode.
- Kimlik doğrulama, çoklu kiracı, rol yönetimi.
- DMS/ProEye/Decisiv entegrasyonu (yalnız "ESCALATE → ProEye" etiketi).
- Geçmiş veriden politika öğrenme (gerçek veri yok; maliyet/güvenilirlik parametreleri uzman varsayımıdır).
- Arıza teşhisi, onarım talimatı üretme, chatbot.

## 6. Başarı metrikleri

**Demo (MVP):**
- Uçtan uca vaka akışı < 2 sn/adım (Jev çağrısı dahil).
- Demo senaryolarında kritik vaka eskalasyon recall = %100.
- Replay ekranı: ServicePilot vs Baseline C (Jev tek-shot) vs Baseline B (sabit checklist) metrikleri.

**PoC (gerçek veriyle, MVP sonrası):** `median time-to-correct-route`, `expert minutes / case`, `additional evidence requests / case`, `first-contact evidence completeness`, `critical escalation recall`, `selective risk @ coverage`.

## 7. Riskler

| Risk | Karşı hamle (MVP) |
|---|---|
| Jev domain kalibrasyonu yetersiz | Eşikler UI'dan ayarlanır; replay ile ölçülür |
| Kritik vakanın otomatik yönlendirilmesi | Safety gate + `critical` noul + yüksek kayıp ağırlığı |
| Maliyet/güvenilirlik parametreleri varsayım | Katalogda açıkça "varsayım" olarak işaretli; PoC'de veriyle güncellenecek |
