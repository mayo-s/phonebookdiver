from unittest.mock import MagicMock

import pytest

import hm_requester


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
