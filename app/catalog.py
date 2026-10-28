"""Domain catalog: expert taxonomy, evidence catalog, safety rules, default policy settings.

Evidence costs (T/E/S), `informs` sets and reliability `rho` are expert ASSUMPTIONS (ADR-5),
to be calibrated with real closed-case data in the PoC.
"""

# Hierarchical expert taxonomy (ARCHITECTURE §4). Leaves are the Jev `route` choice options.
TAXONOMY = {
    "powertrain": {
        "label": "Güç Aktarma",
        "children": {
            "engine": {"label": "Motor (ICE)", "desc": "Diesel engine mechanical faults: overheating, oil/coolant loss, knocking, smoke from exhaust, power loss of mechanical origin, injection and turbo."},
            "transmission": {"label": "Şanzıman / Aktarma", "desc": "Gearbox, clutch, driveline: slipping, hard or delayed shifting, gear noise, transmission warnings."},
        },
    },
    "electrical": {
        "label": "Elektrik",
        "children": {
            "lv_electrical": {"label": "Düşük Voltaj Elektrik", "desc": "12/24V system: batteries, starter motor, alternator, fuses, wiring harness, lighting, no-crank or clicking at start."},
            "ecu_comm": {"label": "ECU / CAN Haberleşme", "desc": "Control units and CAN bus: U-codes, lost communication, multiple unrelated warnings, dashboard/cluster errors, software."},
            "high_voltage": {
                "label": "Yüksek Voltaj",
                "children": {
                    "hv_battery": {"label": "HV Batarya", "desc": "Electric vehicle traction battery: state of charge drop, cell imbalance, battery temperature, isolation faults in the pack."},
                    "hv_charging": {"label": "HV Şarj", "desc": "Electric vehicle charging: charger connection, charge session aborts, onboard charger, charging socket."},
                    "hv_inverter": {"label": "HV İnverter / Motor", "desc": "Electric drive: inverter, traction e-motor, power electronics, loss of propulsion in an electric vehicle."},
                },
            },
        },
    },
    "chassis": {
        "label": "Şasi",
        "children": {
            "brakes": {"label": "Fren / ABS / EBS", "desc": "Air brakes, ABS/EBS, brake pressure, compressor, brake noise or reduced braking."},
            "steering_suspension": {"label": "Direksiyon / Süspansiyon", "desc": "Steering, power steering, suspension, air suspension, vibration and pulling."},
        },
    },
}

ESCALATE_TARGET = "expert_desk"
ESCALATE_LABEL = "Merkez Uzman Masası (ProEye)"


def _walk(tree, parent=None, out=None):
    out = out if out is not None else {}
    for key, node in tree.items():
        out[key] = {"label": node["label"], "parent": parent, "desc": node.get("desc"),
                    "children": list(node.get("children", {}))}
        _walk(node.get("children", {}), key, out)
    return out


NODES = _walk(TAXONOMY)
LEAVES = [k for k, n in NODES.items() if not n["children"]]


def leaves_under(node):
    n = NODES[node]
    return [node] if not n["children"] else [l for c in n["children"] for l in leaves_under(c)]


def ancestors(node):
    out = []
    while (node := NODES[node]["parent"]):
        out.append(node)
    return out


def label(node):
    return ESCALATE_LABEL if node == ESCALATE_TARGET else NODES[node]["label"]


# T: minutes, E: technician effort 1-5, S: safety/operational cost 0-5 (assumptions).
EVIDENCE = {
    "dtc_scan": {"label": "Arıza kodu (DTC) okuma + freeze-frame", "desc": "diagnostic trouble codes read with a scan tool, with freeze-frame data",
                 "T": 5, "E": 1, "S": 0, "rho": 0.6, "informs": ["engine", "transmission", "ecu_comm", "lv_electrical", "hv_inverter", "hv_battery"]},
    "battery_voltage": {"label": "Akü / şarj voltaj ölçümü", "desc": "12/24V battery voltage measured at rest, with ignition on and while cranking",
                        "T": 5, "E": 1, "S": 0, "rho": 0.85, "informs": ["lv_electrical", "ecu_comm"]},
    "connector_photo": {"label": "Konnektör / kablo demeti yakın fotoğrafı", "desc": "close-up photo or visual inspection of the related connector and wiring harness",
                        "T": 3, "E": 1, "S": 0, "rho": 0.5, "informs": ["lv_electrical", "ecu_comm", "hv_charging"]},
    "can_resistance": {"label": "CAN hattı direnç ölçümü (60Ω)", "desc": "CAN bus termination resistance measurement",
                       "T": 15, "E": 3, "S": 0, "rho": 0.9, "informs": ["ecu_comm"]},
    "hv_isolation": {"label": "HV izolasyon direnci ölçümü", "desc": "high-voltage isolation resistance measurement by certified personnel",
                     "T": 30, "E": 4, "S": 4, "rho": 0.85, "informs": ["hv_battery", "hv_inverter"], "requires_ev": True},
    "charging_log": {"label": "Şarj oturumu hata kaydı", "desc": "charging station or onboard charger session error log",
                     "T": 10, "E": 2, "S": 0, "rho": 0.8, "informs": ["hv_charging", "hv_battery"], "requires_ev": True},
    "fluid_check": {"label": "Yağ / soğutma sıvısı kontrolü", "desc": "engine oil and coolant level and condition check",
                    "T": 10, "E": 2, "S": 0, "rho": 0.7, "informs": ["engine"]},
    "trans_log": {"label": "Şanzıman yağ sıcaklığı + vites logu", "desc": "transmission oil temperature and gear shift log",
                  "T": 15, "E": 2, "S": 0, "rho": 0.85, "informs": ["transmission"]},
    "brake_pressure": {"label": "Fren hava basıncı + kaçak testi", "desc": "air brake system pressure and leak test",
                       "T": 20, "E": 3, "S": 1, "rho": 0.9, "informs": ["brakes"]},
    "sound_video": {"label": "Arıza anı ses / video kaydı", "desc": "sound or video recording of the symptom",
                    "T": 5, "E": 1, "S": 0, "rho": 0.5, "informs": ["engine", "transmission", "steering_suspension", "brakes"]},
    "road_test": {"label": "Yol testinde arızayı yeniden üretme", "desc": "road test reproducing the fault",
                  "T": 45, "E": 4, "S": 3, "rho": 0.75, "informs": ["engine", "transmission", "brakes", "steering_suspension"]},
    "service_history": {"label": "Son bakım / onarım geçmişi", "desc": "recent maintenance and repair history of the vehicle",
                        "T": 5, "E": 1, "S": 0, "rho": 0.4, "informs": ["engine", "transmission", "lv_electrical", "brakes", "steering_suspension"]},
}

# Deterministic safety gate (FR-2): lowercase substrings, Turkish + English.
# shortcut: plain substring match without "duman"/"smoke" (exhaust smoke is an engine symptom, not a hazard);
# nuanced hazards are left to Jev `critical`. Upgrade to curated rules with the partner's safety team.
SAFETY_RULES = [
    "yangın", "alev", "yanık kokusu", "fren tutmuyor", "fren boşa", "direksiyon kilit",
    "izolasyon hatası", "izolasyon arızası", "elektrik çarp", "batarya şişme", "termal kaçak",
    "fire", "brake failure", "isolation fault", "thermal runaway",
]

DEFAULT_SETTINGS = {
    "tau_route": 0.80, "tau_suff": 0.60, "tau_crit": 0.75, "lambda": 0.5,
    "alpha": 0.01, "beta": 0.05, "gamma": 0.1, "w_crit": 4.0, "max_requests": 4,
}
