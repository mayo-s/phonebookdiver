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
