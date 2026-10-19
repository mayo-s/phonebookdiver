import time
from unittest.mock import MagicMock

import pytest

import hm_requester

# every test in this file sends real requests to Nominatim
pytestmark = pytest.mark.integration


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
