"""Keep API regressions away from the developer's demo database."""
import pytest
from app import store


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB", tmp_path / "servicepilot.db")
