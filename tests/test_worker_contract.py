import json
from pathlib import Path

from app.catalog import EVIDENCE, LEAVES, SAFETY_RULES
from app.jev import MODEL, URL, build_questions


def test_worker_contract_matches_python_sensor():
    contract = json.loads(Path('worker/contract.json').read_text())
    assert contract == {
        'url': URL, 'model': MODEL, 'questions': build_questions(), 'leaves': LEAVES,
        'evidence': {eid: ev['desc'] for eid, ev in EVIDENCE.items()}, 'safety_rules': SAFETY_RULES,
    }
