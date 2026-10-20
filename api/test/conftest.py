from typing import Iterator
from unittest.mock import MagicMock

import pytest

import helper
import hm_requester
import pymongo


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


TEST_DB = 'phonebookdiver_test'


class CommandLog(pymongo.monitoring.CommandListener):
    """Records every command the client sends, to count real round trips to MongoDB."""

    def __init__(self) -> None:
        self.commands = []

    def started(self, event: pymongo.monitoring.CommandStartedEvent) -> None:
        self.commands.append((event.command_name, event.command.get(event.command_name)))

    def succeeded(self, event: pymongo.monitoring.CommandSucceededEvent) -> None:
        pass

    def failed(self, event: pymongo.monitoring.CommandFailedEvent) -> None:
        pass

    def count(self, command: str, collection: str) -> int:
        return sum(1 for name, target in self.commands if name == command and target == collection)

    def finds_on(self, collection: str) -> int:
        return self.count('find', collection)


@pytest.fixture
def command_log() -> CommandLog:
    return CommandLog()


@pytest.fixture
def mongo_test_db(monkeypatch: pytest.MonkeyPatch, command_log: CommandLog) -> Iterator[pymongo.database.Database]:
    """Point hm_requester at a throwaway database on the local MongoDB, dropped afterwards."""
    client = pymongo.MongoClient(helper.MONGO_URI, serverSelectionTimeoutMS=2000, event_listeners=[command_log])
    try:
        client.admin.command('ping')
    except pymongo.errors.PyMongoError:
        pytest.skip(f'MongoDB not reachable at {helper.MONGO_URI}')
    client.drop_database(TEST_DB)
    db = client[TEST_DB]
    monkeypatch.setattr(hm_requester, 'db', db)
    yield db
    client.drop_database(TEST_DB)
    client.close()
