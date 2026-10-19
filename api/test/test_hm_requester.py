from unittest.mock import MagicMock

import pymongo
import pytest
import requests

import hm_requester


class FakeClock:
    """Stands in for time.monotonic/time.sleep so rate-limit tests never really wait."""

    def __init__(self) -> None:
        self.now = 1000.0
        self.sleeps = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture(autouse=True)
def clock(monkeypatch: pytest.MonkeyPatch) -> FakeClock:
    fake = FakeClock()
    monkeypatch.setattr(hm_requester.time, 'monotonic', fake.monotonic)
    monkeypatch.setattr(hm_requester.time, 'sleep', fake.sleep)
    # start every test as if the last Nominatim request was long ago
    monkeypatch.setattr(hm_requester, 'last_nominatim_request', 0.0)
    return fake


@pytest.fixture
def nominatim(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Replace the HTTP call to Nominatim; returns an empty result by default."""
    get = MagicMock()
    get.return_value.json.return_value = []
    monkeypatch.setattr(hm_requester.requests, 'get', get)
    return get


def test_user_agent_identifies_project_and_contact() -> None:
    user_agent = hm_requester.NOMINATIM_HEADERS['User-Agent']

    assert user_agent.startswith('phonebookdiver/')
    assert 'https://github.com/mayo-s/phonebookdiver' in user_agent


def test_get_coords_sends_user_agent_on_cache_miss(geodata: MagicMock, nominatim: MagicMock) -> None:
    geodata.find_one.return_value = None

    hm_requester.get_coords('19260', 'Marsow', None)

    nominatim.assert_called_once()
    assert nominatim.call_args.kwargs['headers'] == hm_requester.NOMINATIM_HEADERS


def test_get_coords_returns_nominatim_coordinates(geodata: MagicMock, nominatim: MagicMock) -> None:
    geodata.find_one.return_value = None
    nominatim.return_value.json.return_value = [{'lat': '53.4242109', 'lon': '10.9311292'}]

    coords = hm_requester.get_coords('19260', 'Marsow', None)

    assert coords == [53.4242109, 10.9311292]


def test_get_coords_uses_cache_without_request(geodata: MagicMock, nominatim: MagicMock) -> None:
    geodata.find_one.return_value = {'coordinates': [53.4242109, 10.9311292]}

    coords = hm_requester.get_coords('19260', 'Marsow', None)

    assert coords == [53.4242109, 10.9311292]
    nominatim.assert_not_called()


def test_request_nominatim_sets_timeout(nominatim: MagicMock) -> None:
    hm_requester.request_nominatim('19260', 'Marsow')

    assert nominatim.call_args.kwargs['timeout'] == hm_requester.NOMINATIM_TIMEOUT


@pytest.mark.parametrize('failure', [
    requests.ConnectionError('no route to host'),
    requests.Timeout('read timed out'),
])
def test_request_nominatim_returns_empty_list_when_request_fails(nominatim: MagicMock, failure: Exception) -> None:
    nominatim.side_effect = failure

    results = hm_requester.request_nominatim('19260', 'Marsow')

    assert results == []


def test_request_nominatim_returns_empty_list_on_http_error(nominatim: MagicMock) -> None:
    # e.g. 403 Access denied or 429 Too Many Requests
    nominatim.return_value.raise_for_status.side_effect = requests.HTTPError('403 Client Error: Forbidden')

    results = hm_requester.request_nominatim('19260', 'Marsow')

    assert results == []


def test_request_nominatim_returns_empty_list_on_invalid_json(nominatim: MagicMock) -> None:
    nominatim.return_value.json.side_effect = requests.JSONDecodeError('Expecting value', 'Access denied', 0)

    results = hm_requester.request_nominatim('19260', 'Marsow')

    assert results == []


def test_request_nominatim_returns_empty_list_on_unexpected_json(nominatim: MagicMock) -> None:
    nominatim.return_value.json.return_value = {'error': 'Unable to geocode'}

    results = hm_requester.request_nominatim('19260', 'Marsow')

    assert results == []


def test_get_coords_returns_none_instead_of_crashing_when_nominatim_fails(
        geodata: MagicMock, nominatim: MagicMock) -> None:
    geodata.find_one.return_value = None
    nominatim.return_value.json.side_effect = requests.JSONDecodeError('Expecting value', 'Access denied', 0)

    coords = hm_requester.get_coords('19260', 'Marsow', None)

    assert coords is None
    geodata.insert_one.assert_not_called()


def test_first_nominatim_request_does_not_wait(clock: FakeClock, nominatim: MagicMock) -> None:
    hm_requester.request_nominatim('19260', 'Marsow')

    assert clock.sleeps == []


def test_back_to_back_nominatim_requests_wait_one_second(clock: FakeClock, nominatim: MagicMock) -> None:
    hm_requester.request_nominatim('19260', 'Marsow')

    hm_requester.request_nominatim('91541', 'Rothenburg o d Tauber')

    assert clock.sleeps == [pytest.approx(hm_requester.NOMINATIM_MIN_INTERVAL)]


def test_nominatim_request_waits_only_for_remaining_time(clock: FakeClock, nominatim: MagicMock) -> None:
    hm_requester.request_nominatim('19260', 'Marsow')
    clock.now += 0.4

    hm_requester.request_nominatim('91541', 'Rothenburg o d Tauber')

    assert clock.sleeps == [pytest.approx(0.6)]


def test_nominatim_request_after_interval_does_not_wait(clock: FakeClock, nominatim: MagicMock) -> None:
    hm_requester.request_nominatim('19260', 'Marsow')
    clock.now += 1.5

    hm_requester.request_nominatim('91541', 'Rothenburg o d Tauber')

    assert clock.sleeps == []


def test_failed_nominatim_request_still_counts_for_rate_limit(clock: FakeClock, nominatim: MagicMock) -> None:
    nominatim.side_effect = [requests.ConnectionError('no route to host'), MagicMock()]
    hm_requester.request_nominatim('19260', 'Marsow')

    hm_requester.request_nominatim('91541', 'Rothenburg o d Tauber')

    assert clock.sleeps == [pytest.approx(hm_requester.NOMINATIM_MIN_INTERVAL)]


def test_ensure_geodata_indexes_creates_zip_city_and_area_code_index(geodata: MagicMock) -> None:
    hm_requester.ensure_geodata_indexes()

    created = [c.args[0] for c in geodata.create_index.call_args_list]
    assert [('zip', 1), ('city', 1)] in created
    assert 'area_code' in created


def test_ensure_geodata_indexes_keeps_api_running_when_mongodb_is_down(geodata: MagicMock) -> None:
    geodata.create_index.side_effect = pymongo.errors.ServerSelectionTimeoutError('No servers found')

    hm_requester.ensure_geodata_indexes()

    geodata.create_index.assert_called_once()


MARSOW = [53.4242109, 10.9311292]
FLENSBURG = [54.7833021, 9.4333264]


def test_load_geodata_cache_queries_all_zips_in_one_go(geodata: MagicMock) -> None:
    geodata.find.return_value = []
    places = [{'zip': '19260', 'city': 'Marsow'}, {'zip': '24939', 'city': 'Flensburg'},
              {'zip': '19260', 'city': 'Marsow'}]

    hm_requester.load_geodata_cache(places)

    geodata.find.assert_called_once()
    assert sorted(geodata.find.call_args.args[0]['zip']['$in']) == ['19260', '24939']
    geodata.find_one.assert_not_called()


def test_load_geodata_cache_does_not_query_without_places(geodata: MagicMock) -> None:
    hm_requester.load_geodata_cache([])

    geodata.find.assert_not_called()


def test_load_geodata_cache_keys_places_by_zip_and_city_and_by_zip_alone(geodata: MagicMock) -> None:
    geodata.find.return_value = [{'zip': '19260', 'city': 'Marsow', 'coordinates': MARSOW}]

    cache = hm_requester.load_geodata_cache([{'zip': '19260', 'city': 'Marsow'}])

    assert cache['places'][('19260', 'Marsow')] == MARSOW
    assert cache['places'][('19260', None)] == MARSOW


def test_load_geodata_cache_keeps_first_entry_for_duplicate_places(geodata: MagicMock) -> None:
    # geodata holds one entry per area code, so the same zip + city appears several times
    geodata.find.return_value = [
        {'zip': '19260', 'city': 'Marsow', 'coordinates': MARSOW},
        {'zip': '19260', 'city': 'Marsow', 'coordinates': FLENSBURG},
    ]

    cache = hm_requester.load_geodata_cache([{'zip': '19260', 'city': 'Marsow'}])

    assert cache['places'][('19260', 'Marsow')] == MARSOW


def test_load_geodata_cache_queries_area_codes_only_for_places_without_zip(geodata: MagicMock) -> None:
    geodata.find.return_value = []
    places = [
        {'zip': '19260', 'city': 'Marsow', 'area_code': '038852'},
        {'zip': None, 'city': None, 'area_code': '0461'},
        {'zip': None, 'city': None, 'area_code': '0171'},  # mobile prefix, no location
    ]

    hm_requester.load_geodata_cache(places)

    area_code_queries = [c.args[0] for c in geodata.find.call_args_list if 'area_code' in c.args[0]]
    assert area_code_queries == [{'area_code': {'$in': ['0461']}}]


def test_locate_place_uses_cache_without_lookup(geodata: MagicMock, nominatim: MagicMock) -> None:
    cache = {'places': {('19260', 'Marsow'): MARSOW}, 'area_codes': {}}

    coords = hm_requester.locate_place({'zip': '19260', 'city': 'Marsow', 'area_code': '038852'}, cache)

    assert coords == MARSOW
    geodata.find_one.assert_not_called()
    nominatim.assert_not_called()


def test_locate_place_without_city_uses_zip_entry(geodata: MagicMock, nominatim: MagicMock) -> None:
    cache = {'places': {('19260', None): MARSOW}, 'area_codes': {}}

    coords = hm_requester.locate_place({'zip': '19260', 'city': '', 'area_code': None}, cache)

    assert coords == MARSOW
    nominatim.assert_not_called()


def test_locate_place_asks_nominatim_once_per_zip_and_city(geodata: MagicMock, nominatim: MagicMock) -> None:
    # the same place appears once per area code in the grouped search results
    geodata.find_one.return_value = None
    nominatim.return_value.json.return_value = [{'lat': '53.4242109', 'lon': '10.9311292'}]
    cache = {'places': {}, 'area_codes': {}}
    hm_requester.locate_place({'zip': '19260', 'city': 'Marsow', 'area_code': '038852'}, cache)

    coords = hm_requester.locate_place({'zip': '19260', 'city': 'Marsow', 'area_code': '0171'}, cache)

    assert coords == MARSOW
    nominatim.assert_called_once()


def test_locate_place_remembers_unresolved_place_within_search(geodata: MagicMock, nominatim: MagicMock) -> None:
    geodata.find_one.return_value = None
    cache = {'places': {}, 'area_codes': {}}
    hm_requester.locate_place({'zip': '91541', 'city': 'Rothenburg o d Tauber', 'area_code': '09861'}, cache)

    coords = hm_requester.locate_place({'zip': '91541', 'city': 'Rothenburg o d Tauber', 'area_code': '0171'}, cache)

    assert coords is None
    nominatim.assert_called_once()


def test_locate_place_by_area_code_uses_cache(geodata: MagicMock) -> None:
    cache = {'places': {}, 'area_codes': {'0461': FLENSBURG}}

    coords = hm_requester.locate_place({'zip': None, 'city': None, 'area_code': '0461'}, cache)

    assert coords == FLENSBURG
    geodata.find_one.assert_not_called()


@pytest.mark.parametrize('area_code', ['0171', None, '0800'])
def test_locate_place_skips_place_without_zip_and_usable_area_code(area_code: str | None) -> None:
    cache = {'places': {}, 'area_codes': {'0171': MARSOW}}

    coords = hm_requester.locate_place({'zip': None, 'city': None, 'area_code': area_code}, cache)

    assert coords is None


def fake_geodata_find(geodata_docs: list) -> object:
    """db['geodata'].find for the cache queries, which look up a list of zips or area codes with $in."""

    def find(query: dict, projection: dict = None) -> list:
        field = next(iter(query))
        wanted = set(query[field]['$in'])
        return [d for d in geodata_docs if d.get(field) in wanted]

    return find


def test_find_places_matches_the_search_query_first(geodata: MagicMock) -> None:
    query = {'lastname': {'$regex': '^Sch'}}

    hm_requester.find_places('2005_Q1', query)

    pipeline = geodata.aggregate.call_args.args[0]
    assert pipeline[0] == {'$match': query}


def test_find_places_counts_entries_per_zip_city_and_area_code(geodata: MagicMock) -> None:
    hm_requester.find_places('2005_Q1', {'lastname': 'Schütz'})

    group = geodata.aggregate.call_args.args[0][1]['$group']
    assert set(group['_id']) == {'zip', 'city', 'area_code'}
    assert group['count'] == {'$sum': 1}


def test_find_places_returns_grouped_places(geodata: MagicMock) -> None:
    geodata.aggregate.return_value = iter([{'zip': '19260', 'city': 'Marsow', 'area_code': '038852', 'count': 2}])

    places = hm_requester.find_places('2005_Q1', {'lastname': 'Schütz'})

    assert places == [{'zip': '19260', 'city': 'Marsow', 'area_code': '038852', 'count': 2}]


def test_find_places_allows_disk_use_for_large_searches(geodata: MagicMock) -> None:
    hm_requester.find_places('2005_Q1', {'lastname': 'Maier'})

    assert geodata.aggregate.call_args.kwargs['allowDiskUse'] is True


def test_hm_query_returns_coordinates_with_count_per_place(geodata: MagicMock, nominatim: MagicMock) -> None:
    geodata.aggregate.return_value = iter([
        {'zip': '19260', 'city': 'Marsow', 'area_code': '038852', 'count': 2},
        {'zip': '24939', 'city': 'Flensburg', 'area_code': '0461', 'count': 1},
    ])
    geodata.find.side_effect = fake_geodata_find([
        {'zip': '19260', 'city': 'Marsow', 'coordinates': MARSOW},
        {'zip': '24939', 'city': 'Flensburg', 'coordinates': FLENSBURG},
    ])

    positions = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert sorted(positions) == sorted([MARSOW + [2], FLENSBURG + [1]])
    nominatim.assert_not_called()


def test_hm_query_returns_empty_list_without_results(geodata: MagicMock) -> None:
    geodata.aggregate.return_value = iter([])

    positions = hm_requester.hm_query('2005_Q1', {'lastname': 'Gibtesnicht'})

    assert positions == []
    geodata.find.assert_not_called()


def test_hm_query_does_not_write_counts_into_cached_coordinates(geodata: MagicMock) -> None:
    # two area codes for the same zip + city share one cache entry
    geodata_docs = [{'zip': '19260', 'city': 'Marsow', 'coordinates': list(MARSOW)}]
    geodata.aggregate.return_value = iter([
        {'zip': '19260', 'city': 'Marsow', 'area_code': '038852', 'count': 1},
        {'zip': '19260', 'city': 'Marsow', 'area_code': '0171', 'count': 1},
    ])
    geodata.find.side_effect = fake_geodata_find(geodata_docs)

    positions = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert positions == [MARSOW + [1], MARSOW + [1]]
    assert geodata_docs[0]['coordinates'] == MARSOW


def test_hm_query_does_no_single_lookups_when_everything_is_cached(geodata: MagicMock, nominatim: MagicMock) -> None:
    geodata.aggregate.return_value = iter(
        [{'zip': f'{10000 + i}', 'city': f'Ort {i}', 'area_code': '030', 'count': 1} for i in range(500)])
    geodata.find.side_effect = fake_geodata_find(
        [{'zip': f'{10000 + i}', 'city': f'Ort {i}', 'coordinates': [52.0, 13.0]} for i in range(500)])

    positions = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert len(positions) == 500
    geodata.aggregate.assert_called_once()  # the phone book search, grouped in MongoDB
    geodata.find.assert_called_once()  # the geodata cache
    geodata.find_one.assert_not_called()
    nominatim.assert_not_called()
