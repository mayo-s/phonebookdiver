from unittest.mock import MagicMock

import pytest

import hm_requester


@pytest.fixture
def fake_db(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Replace the MongoDB handle; every collection gets its own mock, and no place is known as not found."""
    collections = {}
    db = MagicMock()
    db.__getitem__.side_effect = lambda name: collections.setdefault(name, MagicMock(name=name))
    db[hm_requester.NOT_FOUND].find_one.return_value = None
    db[hm_requester.NOT_FOUND].find.return_value = []
    monkeypatch.setattr(hm_requester, 'db', db)
    return db


@pytest.fixture
def geodata(fake_db: MagicMock) -> MagicMock:
    return fake_db['geodata']


@pytest.fixture
def not_found(fake_db: MagicMock) -> MagicMock:
    return fake_db[hm_requester.NOT_FOUND]


@pytest.fixture
def phonebook(fake_db: MagicMock) -> MagicMock:
    return fake_db['2005_Q1']
