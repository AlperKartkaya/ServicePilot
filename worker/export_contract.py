"""Regenerate the Worker's fixed sensor contract from authoritative Python sources."""
import json
from pathlib import Path

from app.catalog import EVIDENCE, LEAVES, SAFETY_RULES
from app.jev import MODEL, URL, build_questions

contract = {"url": URL, "model": MODEL, "questions": build_questions(), "leaves": LEAVES,
            "evidence": {eid: ev["desc"] for eid, ev in EVIDENCE.items()}, "safety_rules": SAFETY_RULES}
path = Path(__file__).with_name("contract.json")
path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n")
