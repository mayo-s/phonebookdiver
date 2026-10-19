import time
from typing import Iterator
from unittest.mock import MagicMock

import pymongo
import pytest
import requests

import helper
import hm_requester

# every test in this file talks to real services: Nominatim or the local MongoDB
pytestmark = pytest.mark.integration

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


def test_unreachable_server_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    # .invalid never resolves (RFC 2606), so this triggers a real connection error.
    monkeypatch.setattr(hm_requester, 'NOMINATIM_URL', 'https://nominatim.invalid/search.php')

    results = hm_requester.request_nominatim('19260', 'Marsow')

    assert results is None


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


def insert_phonebook(db: pymongo.database.Database, places: int, entries_per_place: int) -> None:
    db['2005_Q1'].insert_many([
        {'lastname': 'Schütz', 'zip': f'{10000 + i}', 'city': f'Ort {i}', 'area_code': '030'}
        for i in range(places) for _ in range(entries_per_place)])
    db['geodata'].insert_many([
        {'zip': f'{10000 + i}', 'city': f'Ort {i}', 'area_code': '030', 'coordinates': [52.0 + i / 1000, 13.0]}
        for i in range(places)])


def test_hm_query_returns_heatmap_positions_from_mongodb(
        mongo_test_db: pymongo.database.Database, no_nominatim: None) -> None:
    hm_requester.ensure_geodata_indexes()
    insert_phonebook(mongo_test_db, places=3, entries_per_place=2)

    positions = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert sorted(positions) == [[52.0, 13.0, 2], [52.001, 13.0, 2], [52.002, 13.0, 2]]


def test_hm_query_loads_cache_with_one_geodata_query(
        mongo_test_db: pymongo.database.Database, command_log: CommandLog, no_nominatim: None) -> None:
    hm_requester.ensure_geodata_indexes()
    insert_phonebook(mongo_test_db, places=300, entries_per_place=1)
    command_log.commands.clear()

    positions = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert len(positions) == 300
    assert command_log.finds_on('geodata') == 1  # was one per place before


def test_hm_query_keeps_cached_coordinates_in_mongodb_unchanged(
        mongo_test_db: pymongo.database.Database, no_nominatim: None) -> None:
    insert_phonebook(mongo_test_db, places=1, entries_per_place=3)

    hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert mongo_test_db['geodata'].find_one({'zip': '10000'})['coordinates'] == [52.0, 13.0]


def places_by_key(places: list) -> dict:
    return {(p['zip'], p['city'], p['area_code']): p['count'] for p in places}


def test_find_places_counts_entries_per_place(mongo_test_db: pymongo.database.Database) -> None:
    mongo_test_db['2005_Q1'].insert_many([
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': '038852'},
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': '038852'},
        {'lastname': 'Schütz', 'zip': '24939', 'city': 'Flensburg', 'area_code': '0461'},
        {'lastname': 'Maier', 'zip': '24939', 'city': 'Flensburg', 'area_code': '0461'},
    ])

    places = hm_requester.find_places('2005_Q1', {'lastname': 'Schütz'})

    assert places_by_key(places) == {('19260', 'Marsow', '038852'): 2, ('24939', 'Flensburg', '0461'): 1}


def test_find_places_groups_zip_and_city_case_insensitively(mongo_test_db: pymongo.database.Database) -> None:
    mongo_test_db['2005_Q1'].insert_many([
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': '038852'},
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'MARSOW', 'area_code': '038852'},
    ])

    places = hm_requester.find_places('2005_Q1', {'lastname': 'Schütz'})

    assert len(places) == 1
    assert places[0]['count'] == 2


def test_find_places_keeps_area_codes_of_one_place_apart(mongo_test_db: pymongo.database.Database) -> None:
    mongo_test_db['2005_Q1'].insert_many([
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': '038852'},
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': '0171'},
    ])

    places = hm_requester.find_places('2005_Q1', {'lastname': 'Schütz'})

    assert places_by_key(places) == {('19260', 'Marsow', '038852'): 1, ('19260', 'Marsow', '0171'): 1}


def test_find_places_turns_missing_area_code_into_empty_string(mongo_test_db: pymongo.database.Database) -> None:
    mongo_test_db['2005_Q1'].insert_many([
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow'},
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': None},
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': ''},
    ])

    places = hm_requester.find_places('2005_Q1', {'lastname': 'Schütz'})

    assert places_by_key(places) == {('19260', 'Marsow', ''): 3}


def test_find_places_supports_regex_search(mongo_test_db: pymongo.database.Database) -> None:
    mongo_test_db['2005_Q1'].insert_many([
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': '038852'},
        {'lastname': 'Schulz', 'zip': '19260', 'city': 'Marsow', 'area_code': '038852'},
        {'lastname': 'Maier', 'zip': '19260', 'city': 'Marsow', 'area_code': '038852'},
    ])

    places = hm_requester.find_places('2005_Q1', {'lastname': {'$regex': '^Sch'}})

    assert places_by_key(places) == {('19260', 'Marsow', '038852'): 2}


def test_find_places_returns_empty_list_without_matches(mongo_test_db: pymongo.database.Database) -> None:
    mongo_test_db['2005_Q1'].insert_one({'lastname': 'Maier', 'zip': '19260', 'city': 'Marsow'})

    places = hm_requester.find_places('2005_Q1', {'lastname': 'Schütz'})

    assert places == []


def test_hm_query_groups_search_in_one_aggregation(
        mongo_test_db: pymongo.database.Database, command_log: CommandLog, no_nominatim: None) -> None:
    insert_phonebook(mongo_test_db, places=50, entries_per_place=4)
    command_log.commands.clear()

    positions = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert len(positions) == 50 and all(p[2] == 4 for p in positions)
    assert command_log.count('aggregate', '2005_Q1') == 1
    assert command_log.finds_on('2005_Q1') == 0  # entries are no longer loaded one by one into Python


class FakeNominatim:
    """Counts requests; answers with Marsow's coordinates unless results or error are changed."""

    def __init__(self) -> None:
        self.requests = 0
        self.results = [{'lat': '53.4242109', 'lon': '10.9311292'}]
        self.error = None

    def get(self, *args: object, **kwargs: object) -> MagicMock:
        self.requests += 1
        if self.error:
            raise self.error
        response = MagicMock()
        response.json.return_value = self.results
        return response


@pytest.fixture
def fake_nominatim(monkeypatch: pytest.MonkeyPatch) -> FakeNominatim:
    fake = FakeNominatim()
    monkeypatch.setattr(hm_requester.requests, 'get', fake.get)
    monkeypatch.setattr(hm_requester, 'NOMINATIM_MIN_INTERVAL', 0.0)
    return fake


def geodata_entries(db: pymongo.database.Database, zip: str) -> list:
    return list(db['geodata'].find({'zip': zip}, {'_id': 0}))


@pytest.mark.parametrize('area_code, saved', [
    ('038852', {'zip': '19260', 'city': 'Marsow', 'coordinates': [53.4242109, 10.9311292], 'area_code': '038852'}),
    ('0171', {'zip': '19260', 'city': 'Marsow', 'coordinates': [53.4242109, 10.9311292]}),
    ('', {'zip': '19260', 'city': 'Marsow', 'coordinates': [53.4242109, 10.9311292]}),
])
def test_get_coords_saves_nominatim_result_in_mongodb(
        mongo_test_db: pymongo.database.Database, fake_nominatim: FakeNominatim, area_code: str, saved: dict) -> None:
    hm_requester.get_coords('19260', 'Marsow', area_code)

    assert geodata_entries(mongo_test_db, '19260') == [saved]


def test_saved_place_is_not_requested_again(
        mongo_test_db: pymongo.database.Database, fake_nominatim: FakeNominatim) -> None:
    hm_requester.get_coords('19260', 'Marsow', '0171')

    coords = hm_requester.get_coords('19260', 'Marsow', '038852')

    assert coords == [53.4242109, 10.9311292]
    assert fake_nominatim.requests == 1
    assert len(geodata_entries(mongo_test_db, '19260')) == 1


def test_save_coords_keeps_one_entry_per_zip_and_city(mongo_test_db: pymongo.database.Database) -> None:
    hm_requester.save_coords('19260', 'Marsow', '038852', [53.4242109, 10.9311292])

    hm_requester.save_coords('19260', 'Marsow', '038852', [1.0, 2.0])

    assert geodata_entries(mongo_test_db, '19260') == [
        {'zip': '19260', 'city': 'Marsow', 'coordinates': [53.4242109, 10.9311292], 'area_code': '038852'}]


def test_mobile_area_code_never_gets_a_location(
        mongo_test_db: pymongo.database.Database, fake_nominatim: FakeNominatim) -> None:
    hm_requester.get_coords('19260', 'Marsow', '0171')

    coords = hm_requester.get_coords_by_area_code('0171')

    assert coords is None


def test_second_heatmap_search_sends_no_nominatim_requests(
        mongo_test_db: pymongo.database.Database, fake_nominatim: FakeNominatim) -> None:
    mongo_test_db['2005_Q1'].insert_many([
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': '038852'},
        {'lastname': 'Schütz', 'zip': '19260', 'city': 'Marsow', 'area_code': '0171'},
        {'lastname': 'Schütz', 'zip': '24939', 'city': 'Flensburg', 'area_code': '0800'},
    ])
    first = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})
    requests_after_first_search = fake_nominatim.requests

    second = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert requests_after_first_search == 2  # one per zip + city
    assert fake_nominatim.requests == requests_after_first_search
    assert sorted(second) == sorted(first)


def test_get_coords_saves_real_nominatim_result_in_mongodb(mongo_test_db: pymongo.database.Database) -> None:
    coords = hm_requester.get_coords('19260', 'Marsow', '0171')

    assert geodata_entries(mongo_test_db, '19260') == [{'zip': '19260', 'city': 'Marsow', 'coordinates': coords}]
    assert coords == pytest.approx([53.42, 10.93], abs=0.05)


def not_found_entries(db: pymongo.database.Database) -> list:
    return list(db[hm_requester.NOT_FOUND].find({}, {'_id': 0, 'checked': 0}))


def test_unknown_place_is_saved_as_not_found(
        mongo_test_db: pymongo.database.Database, fake_nominatim: FakeNominatim) -> None:
    fake_nominatim.results = []

    hm_requester.get_coords('91541', 'Rothenburg o d Tauber', '09861')

    assert not_found_entries(mongo_test_db) == [{'zip': '91541', 'city': 'Rothenburg o d Tauber'}]
    assert mongo_test_db[hm_requester.NOT_FOUND].find_one()['checked'] is not None
    assert geodata_entries(mongo_test_db, '91541') == []


def test_not_found_place_is_not_requested_again(
        mongo_test_db: pymongo.database.Database, fake_nominatim: FakeNominatim) -> None:
    fake_nominatim.results = []
    hm_requester.get_coords('91541', 'Rothenburg o d Tauber', '09861')

    coords = hm_requester.get_coords('91541', 'Rothenburg o d Tauber', '0171')

    assert coords is None
    assert fake_nominatim.requests == 1


def test_temporary_failure_is_retried_on_next_search(
        mongo_test_db: pymongo.database.Database, fake_nominatim: FakeNominatim) -> None:
    fake_nominatim.error = requests.ConnectionError('no route to host')
    hm_requester.get_coords('19260', 'Marsow', '038852')
    fake_nominatim.error = None

    coords = hm_requester.get_coords('19260', 'Marsow', '038852')

    assert coords == [53.4242109, 10.9311292]
    assert fake_nominatim.requests == 2
    assert not_found_entries(mongo_test_db) == []


def test_not_found_place_is_saved_once(mongo_test_db: pymongo.database.Database) -> None:
    hm_requester.ensure_geodata_indexes()
    hm_requester.save_not_found('91541', 'Rothenburg o d Tauber')

    hm_requester.save_not_found('91541', 'Rothenburg o d Tauber')

    assert not_found_entries(mongo_test_db) == [{'zip': '91541', 'city': 'Rothenburg o d Tauber'}]


def test_not_found_index_is_unique(mongo_test_db: pymongo.database.Database) -> None:
    hm_requester.ensure_geodata_indexes()
    mongo_test_db[hm_requester.NOT_FOUND].insert_one({'zip': '91541', 'city': 'Rothenburg o d Tauber'})

    with pytest.raises(pymongo.errors.DuplicateKeyError):
        mongo_test_db[hm_requester.NOT_FOUND].insert_one({'zip': '91541', 'city': 'Rothenburg o d Tauber'})


def test_second_heatmap_search_skips_not_found_places(
        mongo_test_db: pymongo.database.Database, fake_nominatim: FakeNominatim, command_log: CommandLog) -> None:
    fake_nominatim.results = []
    mongo_test_db['2005_Q1'].insert_many([
        {'lastname': 'Schütz', 'zip': '91541', 'city': 'Rothenburg o d Tauber', 'area_code': '09861'},
        {'lastname': 'Schütz', 'zip': '91541', 'city': 'Rothenburg o d Tauber', 'area_code': '0171'},
    ])
    hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})
    command_log.commands.clear()

    positions = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert positions == []
    assert fake_nominatim.requests == 1  # first search only, once per zip + city
    assert command_log.finds_on(hm_requester.NOT_FOUND) == 1  # loaded with the cache, no single lookups


def test_not_found_collection_is_not_listed_as_phonebook(mongo_test_db: pymongo.database.Database) -> None:
    mongo_test_db['2005_Q1'].insert_one({'lastname': 'Schütz'})
    hm_requester.save_coords('19260', 'Marsow', '038852', [53.4242109, 10.9311292])
    hm_requester.save_not_found('91541', 'Rothenburg o d Tauber')

    collections = helper.get_all_collections(mongo_test_db)

    assert list(collections) == ['2005_Q1']


def test_real_nominatim_unknown_place_is_saved_as_not_found(mongo_test_db: pymongo.database.Database) -> None:
    coords = hm_requester.get_coords('00000', 'Gibtesnichthausen', '09861')

    assert coords is None
    assert not_found_entries(mongo_test_db) == [{'zip': '00000', 'city': 'Gibtesnichthausen'}]
