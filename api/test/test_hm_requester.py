from unittest.mock import MagicMock

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
