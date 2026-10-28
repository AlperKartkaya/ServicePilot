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
