from unittest.mock import MagicMock

import pytest

import hm_requester


@pytest.fixture
def geodata(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Replace the MongoDB handle so no test touches the real geodata cache."""
    db = MagicMock()
    monkeypatch.setattr(hm_requester, 'db', db)
    return db['geodata']
