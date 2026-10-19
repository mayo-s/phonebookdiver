import time
from typing import Iterator
from unittest.mock import MagicMock

import pymongo
import pytest

import helper
import hm_requester

# every test in this file talks to real services: Nominatim or the local MongoDB
pytestmark = pytest.mark.integration

TEST_DB = 'phonebookdiver_test'


@pytest.fixture
def mongo_test_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[pymongo.database.Database]:
    """Point hm_requester at a throwaway database on the local MongoDB, dropped afterwards."""
    client = pymongo.MongoClient(helper.MONGO_URI, serverSelectionTimeoutMS=2000)
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


@pytest.fixture
def no_nominatim(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail the test if anything tries to reach Nominatim."""
    def fail(*args: object, **kwargs: object) -> None:
        pytest.fail('unexpected Nominatim request')

    monkeypatch.setattr(hm_requester.requests, 'get', fail)


def test_get_coords_resolves_place_via_real_nominatim(geodata: MagicMock) -> None:
    # Only the geodata cache is mocked, so nothing is written to MongoDB.
    geodata.find_one.return_value = None

    coords = hm_requester.get_coords('19260', 'Marsow', None)

    assert coords == pytest.approx([53.42, 10.93], abs=0.05)


def test_unknown_place_returns_no_results() -> None:
    results = hm_requester.request_nominatim('00000', 'Gibtesnichthausen')

    assert results == []


def test_consecutive_real_requests_are_sent_at_least_one_second_apart(monkeypatch: pytest.MonkeyPatch) -> None:
    sent_at = []
    real_get = hm_requester.requests.get

    def recording_get(*args: object, **kwargs: object) -> object:
        sent_at.append(time.monotonic())
        return real_get(*args, **kwargs)

    monkeypatch.setattr(hm_requester.requests, 'get', recording_get)
    first = hm_requester.request_nominatim('19260', 'Marsow')

    second = hm_requester.request_nominatim('24939', 'Flensburg')

    assert sent_at[1] - sent_at[0] >= hm_requester.NOMINATIM_MIN_INTERVAL
    assert first != [] and second != []


def test_unreachable_server_returns_empty_list(monkeypatch: pytest.MonkeyPatch) -> None:
    # .invalid never resolves (RFC 2606), so this triggers a real connection error.
    monkeypatch.setattr(hm_requester, 'NOMINATIM_URL', 'https://nominatim.invalid/search.php')

    results = hm_requester.request_nominatim('19260', 'Marsow')

    assert results == []


def test_ensure_geodata_indexes_creates_indexes_in_mongodb(mongo_test_db: pymongo.database.Database) -> None:
    hm_requester.ensure_geodata_indexes()

    keys = [index['key'] for index in mongo_test_db['geodata'].index_information().values()]
    assert [('zip', 1), ('city', 1)] in keys
    assert [('area_code', 1)] in keys


def test_ensure_geodata_indexes_can_run_on_every_start(mongo_test_db: pymongo.database.Database) -> None:
    hm_requester.ensure_geodata_indexes()

    hm_requester.ensure_geodata_indexes()

    assert len(mongo_test_db['geodata'].index_information()) == 3  # _id + the two geodata indexes


def test_zip_and_city_lookup_uses_index(mongo_test_db: pymongo.database.Database) -> None:
    hm_requester.ensure_geodata_indexes()

    plan = mongo_test_db['geodata'].find({'zip': '19260', 'city': 'Marsow'}).explain()

    assert 'IXSCAN' in str(plan['queryPlanner']['winningPlan'])


def test_area_code_lookup_uses_index(mongo_test_db: pymongo.database.Database) -> None:
    hm_requester.ensure_geodata_indexes()

    plan = mongo_test_db['geodata'].find({'area_code': '038852'}).explain()

    assert 'IXSCAN' in str(plan['queryPlanner']['winningPlan'])


def test_get_coords_reads_cached_place_from_mongodb(
        mongo_test_db: pymongo.database.Database, no_nominatim: None) -> None:
    hm_requester.ensure_geodata_indexes()
    mongo_test_db['geodata'].insert_one(
        {'zip': '19260', 'city': 'Marsow', 'area_code': '038852', 'coordinates': [53.4242109, 10.9311292]})

    coords = hm_requester.get_coords('19260', 'Marsow', '038852')

    assert coords == [53.4242109, 10.9311292]


def test_get_coords_by_area_code_reads_cached_place_from_mongodb(
        mongo_test_db: pymongo.database.Database, no_nominatim: None) -> None:
    hm_requester.ensure_geodata_indexes()
    mongo_test_db['geodata'].insert_one(
        {'zip': '19260', 'city': 'Marsow', 'area_code': '038852', 'coordinates': [53.4242109, 10.9311292]})

    coords = hm_requester.get_coords_by_area_code('038852')

    assert coords == [53.4242109, 10.9311292]
