"""Demo / replay scenarios (FR-12, FR-13). Synthetic, written for the demo — NOT Anadolu Isuzu data.

`expected` is a taxonomy leaf or "ESCALATE". `answers` simulate the technician's reply per evidence id;
missing ones fall back to NO_FINDING.
"""

NO_FINDING = "Kontrol edildi, belirgin bir bulgu yok / değerler normal."

SCENARIOS = [
    {"id": "lv_starter", "title": "Marş basmıyor, tık tık ses",
     "vehicle": {"family": "Isuzu NPR 10", "fuel": "diesel", "km": 184000},
     "technician_note": "Sabah marşa basınca sadece tık tık ses geliyor, motor dönmüyor. Gösterge ışıkları sönük yanıyor.",
     "dtc_codes": [], "recent_repairs": "", "expected": "lv_electrical",
     "answers": {"battery_voltage": "Kontak kapalı 21.4V, marş anında 14.8V'a düşüyor. Akü kutup başları oksitli.",
                 "connector_photo": "Akü kutup başlarında beyaz oksitlenme var, şase kablosu gevşek."},
     "fixture_signals": {
         "initial": {"route": {"lv_electrical": 0.72, "ecu_comm": 0.16, "engine": 0.12}, "sufficient": 0.38, "critical": 0.06, "priority": {"score": 1.6, "probabilities": {}}, "has": {}},
         "after": {
             "battery_voltage": {"route": {"lv_electrical": 0.94, "ecu_comm": 0.04, "engine": 0.02}, "sufficient": 0.90, "critical": 0.05, "priority": {"score": 1.6, "probabilities": {}}, "has": {"battery_voltage": 0.96}},
             "connector_photo": {"route": {"lv_electrical": 0.91, "ecu_comm": 0.06, "engine": 0.03}, "sufficient": 0.86, "critical": 0.05, "priority": {"score": 1.6, "probabilities": {}}, "has": {"connector_photo": 0.95}},
         },
     }},
    {"id": "can_comm", "title": "Aynı anda çoklu uyarı lambası",
     "vehicle": {"family": "Isuzu Citiport 12", "fuel": "diesel", "km": 412000},
     "technician_note": "Göstergede aynı anda ABS, şanzıman ve motor uyarıları yandı, birkaç saniye sonra söndü. Araç normal sürülüyor.",
     "dtc_codes": ["U0100", "U0121"], "recent_repairs": "Geçen ay gösterge paneli değişti.", "expected": "ecu_comm",
     "answers": {"can_resistance": "CAN-H / CAN-L arası 120Ω ölçüldü (60Ω olmalı); bir sonlandırma direnci devre dışı.",
                 "battery_voltage": "24.6V, normal."},
     "fixture_signals": {
         "initial": {"route": {"ecu_comm": 0.68, "lv_electrical": 0.22, "brakes": 0.06, "transmission": 0.04}, "sufficient": 0.34, "critical": 0.12, "priority": {"score": 1.9, "probabilities": {}}, "has": {"battery_voltage": 0.88, "service_history": 0.82, "connector_photo": 0.85}},
         "after": {
             "can_resistance": {"route": {"ecu_comm": 0.95, "lv_electrical": 0.03, "brakes": 0.01, "transmission": 0.01}, "sufficient": 0.92, "critical": 0.10, "priority": {"score": 1.9, "probabilities": {}}, "has": {"battery_voltage": 0.88, "service_history": 0.82, "connector_photo": 0.85, "can_resistance": 0.98}},
             "battery_voltage": {"route": {"ecu_comm": 0.82, "lv_electrical": 0.12, "brakes": 0.04, "transmission": 0.02}, "sufficient": 0.72, "critical": 0.10, "priority": {"score": 1.9, "probabilities": {}}, "has": {"battery_voltage": 0.96}},
         },
     }},
    {"id": "power_loss", "title": "Yokuşta çekiş kaybı (belirsiz)",
     "vehicle": {"family": "Isuzu Novo Lux", "fuel": "diesel", "km": 265000},
     "technician_note": "Yokuşta çekiş düşüyor, araç ileri gitmekte zorlanıyor.",
     "dtc_codes": [], "recent_repairs": "", "expected": "transmission",
     "answers": {"dtc_scan": "Aktif kod yok; şanzımanda geçmiş P0868 (düşük hat basıncı) kaydı var.",
                 "trans_log": "Şanzıman yağı 118°C'ye çıkıyor, 3-4 vites geçişinde patinaj kaydı var.",
                 "fluid_check": "Motor yağı ve antifriz normal seviyede.",
                 "sound_video": "Hızlanırken devir yükseliyor ama araç hızlanmıyor.",
                 "road_test": "Yokuşta devir 2200'e fırlıyor, hız artmıyor; kavrama/şanzıman kaçırması var."},
     "fixture_signals": {
         "initial": {"route": {"engine": 0.52, "transmission": 0.42, "lv_electrical": 0.06}, "sufficient": 0.22, "critical": 0.10, "priority": {"score": 1.8, "probabilities": {}}, "has": {}},
         "after": {
             "dtc_scan": {"route": {"transmission": 0.76, "engine": 0.20, "lv_electrical": 0.04}, "sufficient": 0.54, "critical": 0.10, "priority": {"score": 1.8, "probabilities": {}}, "has": {"dtc_scan": 0.95}},
             "trans_log": {"route": {"transmission": 0.94, "engine": 0.05, "lv_electrical": 0.01}, "sufficient": 0.91, "critical": 0.10, "priority": {"score": 1.8, "probabilities": {}}, "has": {"dtc_scan": 0.95, "trans_log": 0.96}},
             "sound_video": {"route": {"transmission": 0.86, "engine": 0.12, "lv_electrical": 0.02}, "sufficient": 0.80, "critical": 0.10, "priority": {"score": 1.8, "probabilities": {}}, "has": {"sound_video": 0.95}},
             "fluid_check": {"route": {"transmission": 0.84, "engine": 0.14, "lv_electrical": 0.02}, "sufficient": 0.78, "critical": 0.10, "priority": {"score": 1.8, "probabilities": {}}, "has": {"fluid_check": 0.95}},
             "road_test": {"route": {"transmission": 0.93, "engine": 0.06, "lv_electrical": 0.01}, "sufficient": 0.90, "critical": 0.10, "priority": {"score": 1.8, "probabilities": {}}, "has": {"road_test": 0.96}},
         },
     }},
    {"id": "engine_overheat", "title": "Hararet ve antifriz eksilmesi",
     "vehicle": {"family": "Isuzu N-Wide", "fuel": "diesel", "km": 98000},
     "technician_note": "Uzun yolda hararet göstergesi kırmızıya yaklaşıyor, antifriz eksiliyor.",
     "dtc_codes": ["P0217"], "recent_repairs": "", "expected": "engine",
     "answers": {"fluid_check": "Antifriz minimumun altında, yağda emülsiyon yok, radyatör altında sızıntı izi var."},
     "fixture_signals": {
         "initial": {"route": {"engine": 0.84, "transmission": 0.08, "ecu_comm": 0.05, "lv_electrical": 0.03}, "sufficient": 0.46, "critical": 0.22, "priority": {"score": 2.0, "probabilities": {}}, "has": {}},
         "after": {
             "fluid_check": {"route": {"engine": 0.94, "transmission": 0.03, "ecu_comm": 0.02, "lv_electrical": 0.01}, "sufficient": 0.89, "critical": 0.15, "priority": {"score": 2.0, "probabilities": {}}, "has": {"fluid_check": 0.96}},
         },
     }},
    {"id": "hv_charging", "title": "Şarj 2-3 dakikada kesiliyor",
     "vehicle": {"family": "Isuzu Novociti Volt", "fuel": "electric", "km": 54000},
     "technician_note": "Araç şarja takılıyor ama şarj 2-3 dakika sonra kesiliyor.",
     "dtc_codes": [], "recent_repairs": "", "expected": "hv_charging",
     "answers": {"charging_log": "İstasyon kaydı: 'Vehicle-side contactor open'; oturum 140. saniyede sonlandı. Farklı istasyonda da aynı.",
                 "connector_photo": "Şarj soketinde pin 4'te renk değişimi ve yanma izi."},
     "fixture_signals": {
         "initial": {"route": {"hv_charging": 0.64, "hv_battery": 0.26, "ecu_comm": 0.06, "lv_electrical": 0.04}, "sufficient": 0.32, "critical": 0.16, "priority": {"score": 2.2, "probabilities": {}}, "has": {}},
         "after": {
             "charging_log": {"route": {"hv_charging": 0.76, "hv_battery": 0.14, "lv_electrical": 0.06, "ecu_comm": 0.04}, "sufficient": 0.52, "critical": 0.15, "priority": {"score": 2.2, "probabilities": {}}, "has": {"charging_log": 0.95}},
             "connector_photo": {"route": {"hv_charging": 0.93, "hv_battery": 0.04, "lv_electrical": 0.02, "ecu_comm": 0.01}, "sufficient": 0.90, "critical": 0.14, "priority": {"score": 2.2, "probabilities": {}}, "has": {"charging_log": 0.95, "connector_photo": 0.95}},
         },
     }},
    {"id": "hv_battery", "title": "Menzil düşüşü + batarya sıcaklık uyarısı",
     "vehicle": {"family": "Isuzu Citivolt 12", "fuel": "electric", "km": 76000},
     "technician_note": "Menzil son haftada belirgin düştü, batarya sıcaklık uyarısı ara ara yanıyor.",
     "dtc_codes": [], "recent_repairs": "", "expected": "hv_battery",
     "answers": {"hv_isolation": "İzolasyon direnci 2.4 MΩ, normal.",
                 "charging_log": "Şarj oturumları normal tamamlanıyor; BMS modül 3'te 180 mV hücre dengesizliği uyarısı."},
     "fixture_signals": {
         "initial": {"route": {"hv_battery": 0.62, "hv_charging": 0.22, "hv_inverter": 0.12, "ecu_comm": 0.04}, "sufficient": 0.30, "critical": 0.24, "priority": {"score": 2.1, "probabilities": {}}, "has": {}},
         "after": {
             "charging_log": {"route": {"hv_battery": 0.91, "hv_charging": 0.05, "hv_inverter": 0.03, "ecu_comm": 0.01}, "sufficient": 0.86, "critical": 0.20, "priority": {"score": 2.1, "probabilities": {}}, "has": {"charging_log": 0.96}},
             "hv_isolation": {"route": {"hv_battery": 0.89, "hv_inverter": 0.07, "hv_charging": 0.04}, "sufficient": 0.84, "critical": 0.18, "priority": {"score": 2.1, "probabilities": {}}, "has": {"hv_isolation": 0.96}},
         },
     }},
    {"id": "hv_propulsion", "title": "Kalkışta sarsıntı, çekiş kesiliyor",
     "vehicle": {"family": "Isuzu Citivolt 12", "fuel": "electric", "km": 31000},
     "technician_note": "Araç kalkışta sarsılıyor, bazen çekiş tamamen kesiliyor ve 'sürüş sistemi arızası' uyarısı geliyor.",
     "dtc_codes": ["P0A78"], "recent_repairs": "", "expected": "hv_inverter",
     "answers": {"hv_isolation": "İzolasyon direnci 2.1 MΩ, normal; batarya hücreleri dengeli."},
     "fixture_signals": {
         "initial": {"route": {"hv_inverter": 0.86, "hv_battery": 0.09, "transmission": 0.05}, "sufficient": 0.72, "critical": 0.25, "priority": {"score": 2.3, "probabilities": {}}, "has": {}},
         "after": {
             "hv_isolation": {"route": {"hv_inverter": 0.94, "hv_battery": 0.04, "transmission": 0.02}, "sufficient": 0.91, "critical": 0.18, "priority": {"score": 2.3, "probabilities": {}}, "has": {"hv_isolation": 0.96}},
         },
     }},
    {"id": "intermittent_stall", "title": "Seyirde ara ara stop etme (belirsiz)",
     "vehicle": {"family": "Isuzu NPR 10", "fuel": "diesel", "km": 156000},
     "technician_note": "Araç seyir halindeyken ara ara stop ediyor, birkaç saniye sonra tekrar çalışıyor.",
     "dtc_codes": [], "recent_repairs": "", "expected": "lv_electrical",
     "answers": {"dtc_scan": "Aktif kod yok; geçmişte U3003 (besleme voltajı) kaydı var.",
                 "battery_voltage": "Akü 24.9V normal; stop anında besleme voltajı 9V'a düşüyor.",
                 "connector_photo": "Kontak anahtarı arkasındaki konnektörde gevşeklik ve oksitlenme; konnektör oynatınca gösterge sönüyor.",
                 "fluid_check": "Yağ ve antifriz normal."},
     "fixture_signals": {
         "initial": {"route": {"engine": 0.48, "lv_electrical": 0.36, "ecu_comm": 0.16}, "sufficient": 0.20, "critical": 0.18, "priority": {"score": 2.0, "probabilities": {}}, "has": {}},
         "after": {
             "dtc_scan": {"route": {"lv_electrical": 0.72, "ecu_comm": 0.18, "engine": 0.10}, "sufficient": 0.48, "critical": 0.16, "priority": {"score": 2.0, "probabilities": {}}, "has": {"dtc_scan": 0.95}},
             "battery_voltage": {"route": {"lv_electrical": 0.92, "ecu_comm": 0.05, "engine": 0.03}, "sufficient": 0.88, "critical": 0.14, "priority": {"score": 2.0, "probabilities": {}}, "has": {"dtc_scan": 0.95, "battery_voltage": 0.96}},
             "connector_photo": {"route": {"lv_electrical": 0.94, "ecu_comm": 0.04, "engine": 0.02}, "sufficient": 0.91, "critical": 0.12, "priority": {"score": 2.0, "probabilities": {}}, "has": {"connector_photo": 0.95}},
             "fluid_check": {"route": {"lv_electrical": 0.68, "ecu_comm": 0.20, "engine": 0.12}, "sufficient": 0.45, "critical": 0.16, "priority": {"score": 2.0, "probabilities": {}}, "has": {"fluid_check": 0.95}},
         },
     }},
    {"id": "critical_fire", "title": "Torpido arkasından yanık kokusu",
     "vehicle": {"family": "Isuzu Citiport 12", "fuel": "diesel", "km": 520000},
     "technician_note": "Sürücü torpido arkasından yanık kokusu geldiğini ve hafif duman gördüğünü bildirdi.",
     "dtc_codes": [], "recent_repairs": "", "expected": "ESCALATE", "answers": {},
     "fixture_signals": {
         "initial": {"route": {"lv_electrical": 0.65, "ecu_comm": 0.25, "engine": 0.10}, "sufficient": 0.40, "critical": 0.92, "priority": {"score": 2.9, "probabilities": {}}, "has": {}},
         "after": {},
     }},
    {"id": "critical_brake", "title": "Fren pedalı derine gidiyor",
     "vehicle": {"family": "Isuzu NPR 10", "fuel": "diesel", "km": 230000},
     "technician_note": "Fren pedalı derine gidiyor, araç zor duruyor, hava basıncı uyarısı yanıyor.",
     "dtc_codes": [], "recent_repairs": "", "expected": "ESCALATE", "answers": {},
     "fixture_signals": {
         "initial": {"route": {"brakes": 0.88, "steering_suspension": 0.08, "lv_electrical": 0.04}, "sufficient": 0.55, "critical": 0.89, "priority": {"score": 2.9, "probabilities": {}}, "has": {}},
         "after": {},
     }},
    {"id": "brake_noise", "title": "Frende gıcırtı, performans normal",
     "vehicle": {"family": "Isuzu Novo", "fuel": "diesel", "km": 143000},
     "technician_note": "Frenlemede arka tekerden gıcırtı sesi geliyor, frenleme performansı normal.",
     "dtc_codes": [], "recent_repairs": "", "expected": "brakes",
     "answers": {"brake_pressure": "Sistem basıncı 8.2 bar, kaçak yok. Arka balatalar aşınma sınırında."},
     "fixture_signals": {
         "initial": {"route": {"brakes": 0.85, "steering_suspension": 0.11, "transmission": 0.04}, "sufficient": 0.74, "critical": 0.12, "priority": {"score": 1.3, "probabilities": {}}, "has": {}},
         "after": {
             "brake_pressure": {"route": {"brakes": 0.96, "steering_suspension": 0.03, "transmission": 0.01}, "sufficient": 0.93, "critical": 0.08, "priority": {"score": 1.3, "probabilities": {}}, "has": {"brake_pressure": 0.96}},
         },
     }},
    {"id": "steering_vibration", "title": "Yüksek hızda direksiyon titremesi",
     "vehicle": {"family": "Isuzu Kendo", "fuel": "diesel", "km": 87000},
     "technician_note": "80 km/s üzerinde direksiyonda titreme var, araç hafif sağa çekiyor.",
     "dtc_codes": [], "recent_repairs": "", "expected": "steering_suspension",
     "answers": {"road_test": "80-90 km/s arası titreme belirgin, sağ ön lastikte düzensiz aşınma, rot ayarı bozuk."},
     "fixture_signals": {
         "initial": {"route": {"steering_suspension": 0.86, "brakes": 0.10, "transmission": 0.04}, "sufficient": 0.72, "critical": 0.14, "priority": {"score": 1.5, "probabilities": {}}, "has": {}},
         "after": {
             "road_test": {"route": {"steering_suspension": 0.95, "brakes": 0.03, "transmission": 0.02}, "sufficient": 0.92, "critical": 0.10, "priority": {"score": 1.5, "probabilities": {}}, "has": {"road_test": 0.96}},
         },
     }},
    {"id": "vague_noise", "title": "Garip ses (çok eksik vaka)",
     "vehicle": {"family": "Isuzu Novo", "fuel": "diesel", "km": 301000},
     "technician_note": "Araçta garip bir ses var, müşteri şikayetçi.",
     "dtc_codes": [], "recent_repairs": "", "expected": "engine",
     "answers": {"sound_video": "Ses motor bölmesinden geliyor; rölantide metalik tıkırtı, devirle artıyor.",
                 "dtc_scan": "Aktif kod yok.",
                 "fluid_check": "Motor yağı minimumda ve koyu; antifriz normal.",
                 "road_test": "Tıkırtı motor devriyle artıyor, araç hızından bağımsız."},
     "fixture_signals": {
         "initial": {"route": {"steering_suspension": 0.42, "engine": 0.34, "transmission": 0.24}, "sufficient": 0.15, "critical": 0.08, "priority": {"score": 1.4, "probabilities": {}}, "has": {}},
         "after": {
             "sound_video": {"route": {"engine": 0.76, "transmission": 0.16, "steering_suspension": 0.08}, "sufficient": 0.52, "critical": 0.08, "priority": {"score": 1.4, "probabilities": {}}, "has": {"sound_video": 0.95}},
             "fluid_check": {"route": {"engine": 0.92, "transmission": 0.05, "steering_suspension": 0.03}, "sufficient": 0.88, "critical": 0.08, "priority": {"score": 1.4, "probabilities": {}}, "has": {"sound_video": 0.95, "fluid_check": 0.96}},
             "dtc_scan": {"route": {"engine": 0.88, "transmission": 0.08, "steering_suspension": 0.04}, "sufficient": 0.82, "critical": 0.08, "priority": {"score": 1.4, "probabilities": {}}, "has": {"sound_video": 0.95, "dtc_scan": 0.95}},
             "road_test": {"route": {"engine": 0.93, "transmission": 0.05, "steering_suspension": 0.02}, "sufficient": 0.90, "critical": 0.08, "priority": {"score": 1.4, "probabilities": {}}, "has": {"road_test": 0.96}},
         },
     }},
]


def fixture_signals_for(sc, case):
    """Return deterministic fixture signals for scenario `sc` given collected evidence in `case`."""
    fx = sc.get("fixture_signals") or {}
    ev_list = case.get("evidence") or []
    if not ev_list:
        return fx.get("initial")
    after = fx.get("after") or {}
    for ev in reversed(ev_list):
        if ev["id"] in after:
            return after[ev["id"]]
    return fx.get("initial")

# Inline SVG schematics used as deterministic demo attachments (no external network dependencies).
SVG_CAN = "data:image/svg+xml;utf8," + (
    "<svg xmlns='http://www.w3.org/2000/svg' width='480' height='280' viewBox='0 0 480 280'>"
    "<rect width='480' height='280' fill='%230E141C'/>"
    "<rect x='24' y='24' width='432' height='232' rx='10' fill='%23141C26' stroke='%23253240'/>"
    "<text x='44' y='56' fill='%2396A5B5' font-family='monospace' font-size='12'>OBD-II / CAN HATTI TOPOLOJİ GÖRÜNÜMÜ (DEMO)</text>"
    "<line x1='80' y1='130' x2='400' y2='130' stroke='%2340D9C0' stroke-width='2.5'/>"
    "<line x1='80' y1='160' x2='400' y2='160' stroke='%2379AFFF' stroke-width='2.5'/>"
    "<rect x='60' y='110' width='44' height='70' rx='6' fill='%231B2632' stroke='%2340D9C0'/>"
    "<text x='69' y='149' fill='%23F4F7FA' font-family='monospace' font-size='11'>120Ω</text>"
    "<rect x='210' y='88' width='76' height='32' rx='5' fill='%231B2632' stroke='%23EAB96B'/>"
    "<text x='222' y='108' fill='%23EAB96B' font-family='monospace' font-size='11'>ABS ECU</text>"
    "<rect x='376' y='110' width='44' height='70' rx='6' fill='%231B2632' stroke='%23F17C7C' stroke-dasharray='4 2'/>"
    "<text x='385' y='149' fill='%23F17C7C' font-family='monospace' font-size='11'>AÇIK</text>"
    "<text x='44' y='224' fill='%23F4F7FA' font-family='sans-serif' font-size='13'>Gözlem: Gösterge paneli değişimi sonrası X14 konnektör kilidi tam oturmamış.</text>"
    "</svg>"
)

SVG_HV_SOCKET = "data:image/svg+xml;utf8," + (
    "<svg xmlns='http://www.w3.org/2000/svg' width='480' height='280' viewBox='0 0 480 280'>"
    "<rect width='480' height='280' fill='%230E141C'/>"
    "<rect x='24' y='24' width='432' height='232' rx='10' fill='%23141C26' stroke='%23253240'/>"
    "<text x='44' y='56' fill='%2396A5B5' font-family='monospace' font-size='12'>CCS2 HV ŞARJ SOKETİ ÖN İNCELEME (DEMO)</text>"
    "<circle cx='170' cy='145' r='58' fill='%23090D13' stroke='%23253240' stroke-width='2'/>"
    "<circle cx='150' cy='130' r='10' fill='%231B2632' stroke='%2396A5B5'/>"
    "<circle cx='190' cy='130' r='10' fill='%231B2632' stroke='%2396A5B5'/>"
    "<circle cx='152' cy='168' r='14' fill='%231B2632' stroke='%2340D9C0'/>"
    "<circle cx='188' cy='168' r='14' fill='%233A1D24' stroke='%23F17C7C' stroke-width='2.5'/>"
    "<text x='255' y='125' fill='%23F4F7FA' font-family='sans-serif' font-size='13' font-weight='bold'>DC+ Pin 4 Termal İz Şüphesi</text>"
    "<text x='255' y='150' fill='%2396A5B5' font-family='sans-serif' font-size='12'>Oturum 140. sn'de kontaktör açıyor.</text>"
    "<text x='255' y='172' fill='%23EAB96B' font-family='monospace' font-size='12'>İstenen: Yakın plan makro fotoğraf</text>"
    "</svg>"
)

SVG_RADIATOR = "data:image/svg+xml;utf8," + (
    "<svg xmlns='http://www.w3.org/2000/svg' width='480' height='280' viewBox='0 0 480 280'>"
    "<rect width='480' height='280' fill='%230E141C'/>"
    "<rect x='24' y='24' width='432' height='232' rx='10' fill='%23141C26' stroke='%23253240'/>"
    "<text x='44' y='56' fill='%2396A5B5' font-family='monospace' font-size='12'>SOĞUTMA HATTI &amp; GENLEŞME KABI KONTROLÜ (DEMO)</text>"
    "<rect x='70' y='82' width='120' height='130' rx='8' fill='%23090D13' stroke='%23253240'/>"
    "<line x1='78' y1='115' x2='182' y2='115' stroke='%2396A5B5' stroke-dasharray='4 4'/>"
    "<text x='86' y='110' fill='%2396A5B5' font-family='monospace' font-size='10'>MIN SEVİYE</text>"
    "<rect x='74' y='150' width='112' height='58' rx='4' fill='%231B2632'/>"
    "<line x1='74' y1='150' x2='186' y2='150' stroke='%23F17C7C' stroke-width='2'/>"
    "<text x='220' y='125' fill='%23F4F7FA' font-family='sans-serif' font-size='13'>Antifriz seviyesi MIN çizgisinin 3 cm altında</text>"
    "<text x='220' y='152' fill='%2340D9C0' font-family='monospace' font-size='12'>Yağda emülsiyon yok · Alt kelepçe sızıntısı</text>"
    "<text x='220' y='178' fill='%2396A5B5' font-family='sans-serif' font-size='12'>DTC: P0217 (Motor Aşırı Isınma Koşulu)</text>"
    "</svg>"
)

SVG_BATTERY = "data:image/svg+xml;utf8," + (
    "<svg xmlns='http://www.w3.org/2000/svg' width='480' height='280' viewBox='0 0 480 280'>"
    "<rect width='480' height='280' fill='%230E141C'/>"
    "<rect x='24' y='24' width='432' height='232' rx='10' fill='%23141C26' stroke='%23253240'/>"
    "<text x='44' y='56' fill='%2396A5B5' font-family='monospace' font-size='12'>24V AKÜ GRUBU GERİLİM DÜŞÜMÜ TESTİ (DEMO)</text>"
    "<polyline points='60,110 160,110 185,195 230,190 260,135 410,135' fill='none' stroke='%2340D9C0' stroke-width='3'/>"
    "<text x='65' y='98' fill='%23F4F7FA' font-family='monospace' font-size='12'>Dinlenme: 21.4V</text>"
    "<text x='170' y='218' fill='%23F17C7C' font-family='monospace' font-size='12'>Marş Anı: 14.8V (Kritik Düşüm)</text>"
    "<text x='44' y='242' fill='%2396A5B5' font-family='sans-serif' font-size='12'>Kutup başlarında oksitlenme ve gevşek şase bağlantısı doğrulandı.</text>"
    "</svg>"
)


def build_demo_cases(decide_fn, settings):
    """Build 5 deterministic representative demo cases using the real RAEP engine (FR-20)."""
    specs = [
        {
            "id": "SP-0001",
            "created_at": "2026-10-28T08:15:00+00:00",
            "updated_at": "2026-10-28T08:16:00+00:00",
            "scenario_id": "can_comm",
            "vehicle": {
                "family": "Isuzu Citiport 12",
                "fuel": "diesel",
                "km": 412000,
                "vin": "NLNC12000R0041892",
                "location": "İstanbul İkitelli Yetkili Servis",
            },
            "technician_note": "Göstergede seyir halinde aynı anda ABS, şanzıman ve motor arıza uyarı lambaları yandı, birkaç saniye sonra kendiliğinden söndü. Araç çekişinde ve frenlemesinde anlık bir kesinti hissedilmedi.",
            "initial_measurements": "Akü dinlenme voltajı 24.6V (normal). Gösterge konnektörü X14 çevresinde kablo demeti gergin duruyor.",
            "dtc_codes": ["U0100", "U0121"],
            "recent_repairs": "Geçen ay gösterge paneli modülü (cluster) garantiden değişti.",
            "attachments": [
                {"name": "citiport-can-topoloji.svg", "caption": "Gösterge paneli arkası X14 konnektör ve CAN hattı kontrol şeması", "data_url": SVG_CAN}
            ],
            "evidence": [],
            "step_specs": [
                {
                    "at": "2026-10-28T08:15:12+00:00",
                    "latency_ms": 384,
                    "signals": {
                        "route": {"ecu_comm": 0.68, "lv_electrical": 0.22, "brakes": 0.06, "transmission": 0.03, "engine": 0.01},
                        "sufficient": 0.34,
                        "critical": 0.12,
                        "priority": {"score": 1.9, "probabilities": {"0": 0.05, "1": 0.25, "2": 0.45, "3": 0.25}},
                        "has": {"battery_voltage": 0.88, "service_history": 0.82, "connector_photo": 0.85},
                    },
                }
            ],
            "review_status": None,
            "audit": [
                {"at": "2026-10-28T08:15:00+00:00", "actor": "Teknisyen (İkitelli Servis)", "action": "Vaka Oluşturuldu", "detail": "U0100 ve U0121 DTC kodları ve ilk voltaj gözlemi ile kayıt açıldı."},
                {"at": "2026-10-28T08:15:12+00:00", "actor": "ServicePilot (RAEP)", "action": "Eksik Kanıt İstendi", "detail": "ECU / CAN Haberleşme olasılığı (0.68) yönlendirme eşiğinin (0.80) altında. En yüksek net fayda sağlayan 'CAN hattı direnç ölçümü (60Ω)' talep edildi."},
            ],
        },
        {
            "id": "SP-0002",
            "created_at": "2026-10-28T09:05:00+00:00",
            "updated_at": "2026-10-28T09:22:00+00:00",
            "scenario_id": "hv_charging",
            "vehicle": {
                "family": "Isuzu Novociti Volt",
                "fuel": "electric",
                "km": 54000,
                "vin": "NLNEV0800S0010421",
                "location": "İzmir Bornova Yetkili Servis",
            },
            "technician_note": "Araç CCS2 DC hızlı şarja takılıyor, el sıkışma tamamlanıyor ancak şarj başladıktan 2-3 dakika sonra oturum aniden kesiliyor.",
            "initial_measurements": "Farklı bir şarj istasyonunda denendi, aynı şekilde 2. dakikada kesildi.",
            "dtc_codes": ["P0AA6"],
            "recent_repairs": "2 hafta önce şarj soketi koruma kapağı menteşesi yenilendi.",
            "attachments": [
                {"name": "ccs2-soket-on-inceleme.svg", "caption": "CCS2 şarj soketi pin yerleşimi ve termal kontrol noktası", "data_url": SVG_HV_SOCKET}
            ],
            "evidence": [
                {
                    "id": "charging_log",
                    "label": "Şarj oturumu hata kaydı",
                    "result": "İstasyon kaydı: 'Vehicle-side contactor open'; oturum 140. saniyede sonlandı. Pilot sinyali kopması görülüyor.",
                    "at": "2026-10-28T09:20:00+00:00",
                }
            ],
            "step_specs": [
                {
                    "at": "2026-10-28T09:05:10+00:00",
                    "latency_ms": 410,
                    "signals": {
                        "route": {"hv_charging": 0.58, "hv_battery": 0.30, "ecu_comm": 0.08, "lv_electrical": 0.04},
                        "sufficient": 0.28,
                        "critical": 0.18,
                        "priority": {"score": 2.2, "probabilities": {"0": 0.0, "1": 0.15, "2": 0.50, "3": 0.35}},
                        "has": {},
                    },
                },
                {
                    "at": "2026-10-28T09:20:15+00:00",
                    "latency_ms": 395,
                    "signals": {
                        "route": {"hv_charging": 0.75, "hv_battery": 0.14, "lv_electrical": 0.07, "ecu_comm": 0.04},
                        "sufficient": 0.48,
                        "critical": 0.16,
                        "priority": {"score": 2.2, "probabilities": {"0": 0.0, "1": 0.15, "2": 0.50, "3": 0.35}},
                        "has": {"charging_log": 0.95},
                    },
                },
            ],
            "review_status": None,
            "audit": [
                {"at": "2026-10-28T09:05:00+00:00", "actor": "Teknisyen (Bornova Servis)", "action": "Vaka Oluşturuldu", "detail": "Novociti Volt DC şarj kesintisi bildirimiyle açıldı."},
                {"at": "2026-10-28T09:20:00+00:00", "actor": "Teknisyen (Bornova Servis)", "action": "Kanıt Eklendi", "detail": "Şarj oturumu hata kaydı girildi (140. sn kontaktör açma)."},
                {"at": "2026-10-28T09:20:15+00:00", "actor": "ServicePilot (RAEP)", "action": "Görsel Kanıt İstendi", "detail": "Soket kaynaklı temassızlığı batarya paketinden ayırmak için 'Konnektör / kablo demeti yakın fotoğrafı' talep edildi."},
            ],
        },
        {
            "id": "SP-0003",
            "created_at": "2026-10-28T10:12:00+00:00",
            "updated_at": "2026-10-28T10:12:05+00:00",
            "scenario_id": "critical_fire",
            "vehicle": {
                "family": "Isuzu Citiport 12",
                "fuel": "diesel",
                "km": 520000,
                "vin": "NLNC12000P0038910",
                "location": "Ankara Merkez Yetkili Servis",
            },
            "technician_note": "Sürücü seyir halindeyken torpido arkasından keskin yanık kokusu geldiğini ve sağ havalandırma menfezinden hafif duman çıktığını bildirdi. Araç güvenlik prosedürü gereği stop edilip akü şalteri kapatıldı.",
            "initial_measurements": "Kabin içi sigorta tablası F18-F22 hattında aşırı ısınma izi var; araca enerji verilmedi.",
            "dtc_codes": ["B1004"],
            "recent_repairs": "6 ay önce kabin kalorifer fan rezistansı değişti.",
            "attachments": [],
            "evidence": [],
            "step_specs": [
                {
                    "at": "2026-10-28T10:12:02+00:00",
                    "latency_ms": 0,
                    "signals": None,
                }
            ],
            "review_status": "pending_review",
            "audit": [
                {"at": "2026-10-28T10:12:00+00:00", "actor": "Teknisyen (Ankara Servis)", "action": "Vaka Oluşturuldu", "detail": "Torpido arkası yanık kokusu ve duman bildirimi kaydedildi."},
                {"at": "2026-10-28T10:12:02+00:00", "actor": "ServicePilot (Safety Gate)", "action": "Kritik Eskalasyon", "detail": "Deterministik güvenlik kuralı ('yanık kokusu') tetiklendi. Otomatik yönlendirme engellenerek Merkez Uzman Masası (ProEye) onayına gönderildi."},
            ],
        },
        {
            "id": "SP-0004",
            "created_at": "2026-10-28T11:00:00+00:00",
            "updated_at": "2026-10-28T11:18:00+00:00",
            "scenario_id": "engine_overheat",
            "vehicle": {
                "family": "Isuzu N-Wide",
                "fuel": "diesel",
                "km": 98000,
                "vin": "NLNNWD000R0082315",
                "location": "Bursa Yetkili Servis",
            },
            "technician_note": "Uzun yolda yük altında hararet göstergesi kırmızı bölgeye yaklaşıyor, genleşme kabında antifriz seviyesi sürekli eksiliyor.",
            "initial_measurements": "Rölantide fan devreye giriyor, kabin ısıtması normal.",
            "dtc_codes": ["P0217"],
            "recent_repairs": "90.000 km periyodik bakımı yetkili serviste yapıldı.",
            "attachments": [
                {"name": "n-wide-sogutma-kontrol.svg", "caption": "Genleşme kabı seviye kontrolü ve alt radyatör hortumu sızıntı tespiti", "data_url": SVG_RADIATOR}
            ],
            "evidence": [
                {
                    "id": "fluid_check",
                    "label": "Yağ / soğutma sıvısı kontrolü",
                    "result": "Antifriz minimumun 3 cm altında, motor yağında emülsiyon yok, radyatör alt hortum kelepçesinde sızıntı izi var.",
                    "at": "2026-10-28T11:17:00+00:00",
                }
            ],
            "step_specs": [
                {
                    "at": "2026-10-28T11:00:08+00:00",
                    "latency_ms": 372,
                    "signals": {
                        "route": {"engine": 0.84, "transmission": 0.08, "ecu_comm": 0.05, "lv_electrical": 0.03},
                        "sufficient": 0.46,
                        "critical": 0.22,
                        "priority": {"score": 2.0, "probabilities": {"0": 0.05, "1": 0.20, "2": 0.50, "3": 0.25}},
                        "has": {},
                    },
                },
                {
                    "at": "2026-10-28T11:17:14+00:00",
                    "latency_ms": 358,
                    "signals": {
                        "route": {"engine": 0.93, "transmission": 0.04, "ecu_comm": 0.02, "lv_electrical": 0.01},
                        "sufficient": 0.89,
                        "critical": 0.15,
                        "priority": {"score": 2.0, "probabilities": {"0": 0.05, "1": 0.20, "2": 0.50, "3": 0.25}},
                        "has": {"fluid_check": 0.96},
                    },
                },
            ],
            "review_status": "pending_confirmation",
            "audit": [
                {"at": "2026-10-28T11:00:00+00:00", "actor": "Teknisyen (Bursa Servis)", "action": "Vaka Oluşturuldu", "detail": "P0217 hararet uyarısı ve antifriz eksiltme şikayetiyle açıldı."},
                {"at": "2026-10-28T11:17:00+00:00", "actor": "Teknisyen (Bursa Servis)", "action": "Kanıt Eklendi", "detail": "Yağ / soğutma sıvısı kontrolü sonucu ve sızıntı bulgusu eklendi."},
                {"at": "2026-10-28T11:17:14+00:00", "actor": "ServicePilot (RAEP)", "action": "Yönlendirme Önerildi", "detail": "Motor (ICE) olasılığı (0.93) ve kanıt yeterliliği (0.89) eşikleri geçti. Yönlendirme onayı bekleniyor."},
            ],
        },
        {
            "id": "SP-0005",
            "created_at": "2026-10-28T07:30:00+00:00",
            "updated_at": "2026-10-28T07:50:00+00:00",
            "scenario_id": "lv_starter",
            "vehicle": {
                "family": "Isuzu NPR 10",
                "fuel": "diesel",
                "km": 184000,
                "vin": "NLNNPR100P0064119",
                "location": "Kocaeli Gebze Yetkili Servis",
            },
            "technician_note": "Sabah ilk çalıştırmada marşa basınca sadece tık tık ses geliyor, motor dönmüyor. Gösterge ışıkları marş anında belirgin şekilde sönükleşiyor.",
            "initial_measurements": "Marş rölesi çekiyor ancak marş motoru kavramıyor.",
            "dtc_codes": ["P0562"],
            "recent_repairs": "Orijinal aküler 36 aydır araç üzerinde.",
            "attachments": [
                {"name": "npr10-aku-voltaj-testi.svg", "caption": "24V akü grubu marş anı gerilim düşümü grafiği", "data_url": SVG_BATTERY}
            ],
            "evidence": [
                {
                    "id": "battery_voltage",
                    "label": "Akü / şarj voltaj ölçümü",
                    "result": "Kontak kapalı 21.4V, marş anında 14.8V'a düşüyor. Akü kutup başları oksitli.",
                    "at": "2026-10-28T07:42:00+00:00",
                }
            ],
            "step_specs": [
                {
                    "at": "2026-10-28T07:30:09+00:00",
                    "latency_ms": 365,
                    "signals": {
                        "route": {"lv_electrical": 0.78, "ecu_comm": 0.12, "engine": 0.10},
                        "sufficient": 0.42,
                        "critical": 0.05,
                        "priority": {"score": 1.6, "probabilities": {"0": 0.10, "1": 0.40, "2": 0.35, "3": 0.15}},
                        "has": {},
                    },
                },
                {
                    "at": "2026-10-28T07:42:11+00:00",
                    "latency_ms": 340,
                    "signals": {
                        "route": {"lv_electrical": 0.95, "ecu_comm": 0.03, "engine": 0.02},
                        "sufficient": 0.92,
                        "critical": 0.04,
                        "priority": {"score": 1.6, "probabilities": {"0": 0.10, "1": 0.40, "2": 0.35, "3": 0.15}},
                        "has": {"battery_voltage": 0.98},
                    },
                },
            ],
            "review_status": "confirmed",
            "audit": [
                {"at": "2026-10-28T07:30:00+00:00", "actor": "Teknisyen (Gebze Servis)", "action": "Vaka Oluşturuldu", "detail": "NPR 10 marş basmama ve P0562 düşük sistem voltajı koduyla açıldı."},
                {"at": "2026-10-28T07:42:00+00:00", "actor": "Teknisyen (Gebze Servis)", "action": "Kanıt Eklendi", "detail": "Akü / şarj voltaj ölçümü (21.4V → marşta 14.8V) sisteme girildi."},
                {"at": "2026-10-28T07:42:11+00:00", "actor": "ServicePilot (RAEP)", "action": "Otomatik Yönlendirme", "detail": "Düşük Voltaj Elektrik uzmanlığına yönlendirme önerildi (p=0.95, yeterlilik=0.92)."},
                {"at": "2026-10-28T07:50:00+00:00", "actor": "Servis Sorumlusu", "action": "Yönlendirme Onaylandı", "detail": "Vaka Düşük Voltaj Elektrik uzman ekibine kesin olarak atandı."},
            ],
        },
    ]

    status_map = {"ROUTE": "routed", "ESCALATE": "escalated", "REQUEST_EVIDENCE": "awaiting_evidence"}
    out = []
    for sp in specs:
        case = {
            "id": sp["id"],
            "created_at": sp["created_at"],
            "updated_at": sp["updated_at"],
            "status": "awaiting_evidence",
            "review_status": sp["review_status"],
            "scenario_id": sp["scenario_id"],
            "vehicle": sp["vehicle"],
            "technician_note": sp["technician_note"],
            "initial_measurements": sp["initial_measurements"],
            "dtc_codes": sp["dtc_codes"],
            "recent_repairs": sp["recent_repairs"],
            "attachments": sp["attachments"],
            "evidence": [],
            "pending_evidence": None,
            "steps": [],
            "audit": sp["audit"],
            "final": None,
            "is_demo": True,
        }
        for idx, st_spec in enumerate(sp["step_specs"]):
            if idx > 0 and idx - 1 < len(sp["evidence"]):
                case["evidence"].append(sp["evidence"][idx - 1])
            d = decide_fn(case, st_spec["signals"], settings)
            case["steps"].append({
                "at": st_spec["at"],
                "latency_ms": st_spec["latency_ms"],
                "signals": st_spec["signals"],
                "settings": dict(settings),
                "decision": d,
            })
            case["status"] = status_map[d["action"]]
            case["pending_evidence"] = d["evidence_id"]
            case["final"] = None if d["action"] == "REQUEST_EVIDENCE" else {k: d[k] for k in ("action", "target", "target_label")}
        out.append(case)
    return out

