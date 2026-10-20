from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts import geodata_cleanup as cleanup
import hm_requester

GALMSBUELL = [54.7685346, 8.7919715]  # centre of zip 25899
NIEBUELL = [54.7868097, 8.8258359]
FRANCE = [47.8091066, 6.8970628]  # where Flühe 25899 was geocoded
OBERSTDORF = [47.4088967, 10.2202678]  # Nominatim's answer for postcode 25899 + "Flühe"
VIENNA = [48.2082, 16.3738]


class FakeNominatimSearch:
    """Postcode-only queries get the zip centre, postcode + city queries get city_results."""

    def __init__(self) -> None:
        self.centre_results = [{'lat': str(GALMSBUELL[0]), 'lon': str(GALMSBUELL[1])}]
        self.city_results = []
        self.calls = []

    def __call__(self, params: dict) -> list | None:
        self.calls.append(params)
        return self.city_results if 'city' in params else self.centre_results


def result(coords: list) -> list:
    return [{'lat': str(coords[0]), 'lon': str(coords[1])}]


@pytest.fixture
def search(monkeypatch: pytest.MonkeyPatch) -> FakeNominatimSearch:
    fake = FakeNominatimSearch()
    monkeypatch.setattr(hm_requester, 'nominatim_search', fake)
    return fake


def test_places_by_zip_groups_real_postcodes_only(geodata: MagicMock) -> None:
    geodata.find.return_value = [
        {'zip': '25899', 'city': 'Niebüll', 'coordinates': NIEBUELL},
        {'zip': '25899', 'city': 'Niebüll', 'coordinates': NIEBUELL},  # one entry per area code
        {'zip': '25899', 'city': 'Flühe', 'coordinates': FRANCE},
        {'zip': '.....', 'city': 'Petershagen/Eggersdorf', 'coordinates': [52.52, 13.77]},
        {'zip': '25899', 'city': 'Dagebüll'},
    ]

    zips = cleanup.places_by_zip()

    assert dict(zips) == {'25899': {('Niebüll', tuple(NIEBUELL)), ('Flühe', tuple(FRANCE))}}


def test_zip_with_a_far_away_place_is_suspect() -> None:
    places = {('Niebüll', tuple(NIEBUELL)), ('Galmsbüll', tuple(GALMSBUELL)), ('Flühe', tuple(FRANCE))}

    assert cleanup.is_suspect(places)


def test_zip_with_close_places_is_not_suspect() -> None:
    places = {('Niebüll', tuple(NIEBUELL)), ('Galmsbüll', tuple(GALMSBUELL))}

    assert not cleanup.is_suspect(places)


def test_zip_with_a_single_place_is_not_suspect() -> None:
    assert not cleanup.is_suspect({('Flühe', tuple(FRANCE))})


def test_find_suspect_zips_returns_sorted_zips() -> None:
    zips = {
        '25899': {('Niebüll', tuple(NIEBUELL)), ('Flühe', tuple(FRANCE))},
        '19260': {('Marsow', (53.4242109, 10.9311292)), ('Vellahn', (53.3959, 10.9611))},
        '16818': {('Werder', tuple(GALMSBUELL)), ('Kränzlin', (52.9536, 12.8139))},
    }

    assert cleanup.find_suspect_zips(zips) == ['16818', '25899']


def test_zip_centre_asks_for_postcode_only(search: FakeNominatimSearch) -> None:
    centre = cleanup.zip_centre('25899')

    assert centre == GALMSBUELL
    assert search.calls == [{'postalcode': '25899', 'country': 'de', 'format': 'jsonv2'}]


@pytest.mark.parametrize('centre_results', [None, [], result(VIENNA)])
def test_zip_centre_is_none_without_usable_result(search: FakeNominatimSearch, centre_results: list | None) -> None:
    search.centre_results = centre_results

    assert cleanup.zip_centre('25899') is None


def test_regeocode_asks_for_postcode_and_city(search: FakeNominatimSearch) -> None:
    search.city_results = result(NIEBUELL)

    coords = cleanup.regeocode('25899', 'Niebüll', GALMSBUELL)

    assert coords == NIEBUELL
    assert search.calls == [{'postalcode': '25899', 'city': 'Niebüll', 'country': 'de', 'format': 'jsonv2'}]


@pytest.mark.parametrize('city_results', [result(OBERSTDORF), result(VIENNA), [], None])
def test_regeocode_rejects_result_not_close_to_centre(search: FakeNominatimSearch, city_results: list | None) -> None:
    search.city_results = city_results

    assert cleanup.regeocode('25899', 'Flühe', GALMSBUELL) is None


def test_plan_entry_skips_place_close_to_centre(search: FakeNominatimSearch) -> None:
    row = cleanup.plan_entry('25899', 'Niebüll', tuple(NIEBUELL), GALMSBUELL)

    assert row is None
    assert search.calls == []


def test_plan_entry_updates_wrong_place_that_can_be_regeocoded(search: FakeNominatimSearch) -> None:
    search.city_results = result([54.75, 8.80])

    row = cleanup.plan_entry('25899', 'Flühe', tuple(FRANCE), GALMSBUELL)

    assert row['action'] == cleanup.UPDATE
    assert (row['old_lat'], row['old_lon']) == tuple(FRANCE)
    assert (row['new_lat'], row['new_lon']) == (54.75, 8.80)
    assert row['km_from_centre'] == round(hm_requester.distance_km(FRANCE, GALMSBUELL))


def test_plan_entry_moves_wrong_place_that_cannot_be_regeocoded(search: FakeNominatimSearch) -> None:
    search.city_results = result(OBERSTDORF)

    row = cleanup.plan_entry('25899', 'Flühe', tuple(FRANCE), GALMSBUELL)

    assert row['action'] == cleanup.MOVE
    assert (row['new_lat'], row['new_lon']) == ('', '')


def test_plan_entry_without_city_moves_without_request(search: FakeNominatimSearch) -> None:
    row = cleanup.plan_entry('25899', None, tuple(FRANCE), GALMSBUELL)

    assert row['action'] == cleanup.MOVE
    assert row['city'] == ''
    assert search.calls == []


def test_plan_zip_skips_zip_without_centre(search: FakeNominatimSearch) -> None:
    search.centre_results = []

    rows = cleanup.plan_zip('25899', {('Flühe', tuple(FRANCE))})

    assert rows == []
    assert len(search.calls) == 1


def test_plan_zip_lists_only_wrong_places(search: FakeNominatimSearch) -> None:
    places = {('Niebüll', tuple(NIEBUELL)), ('Galmsbüll', tuple(GALMSBUELL)), ('Flühe', tuple(FRANCE))}

    rows = cleanup.plan_zip('25899', places)

    assert [(r['city'], r['action']) for r in rows] == [('Flühe', cleanup.MOVE)]


def test_plan_csv_keeps_coordinates_exact(tmp_path: Path) -> None:
    rows = [{'zip': '25899', 'city': 'Flühe', 'old_lat': FRANCE[0], 'old_lon': FRANCE[1], 'km_from_centre': 790,
             'action': cleanup.UPDATE, 'new_lat': 54.7500001, 'new_lon': 8.8000002}]
    cleanup.write_plan(tmp_path / 'plan.csv', rows)

    read = cleanup.read_plan(tmp_path / 'plan.csv')

    assert [float(read[0]['old_lat']), float(read[0]['old_lon'])] == FRANCE
    assert [float(read[0]['new_lat']), float(read[0]['new_lon'])] == [54.7500001, 8.8000002]
    assert read[0]['city'] == 'Flühe'


def plan_row(action: str, city: str = 'Flühe') -> dict:
    """A row as read back from the CSV, so every value is a string."""
    new = ('54.75', '8.8') if action == cleanup.UPDATE else ('', '')
    return {'zip': '25899', 'city': city, 'old_lat': str(FRANCE[0]), 'old_lon': str(FRANCE[1]), 'km_from_centre': '790',
            'action': action, 'new_lat': new[0], 'new_lon': new[1]}


def test_entry_filter_matches_old_coordinates() -> None:
    assert cleanup.entry_filter(plan_row(cleanup.UPDATE)) == {'zip': '25899', 'city': 'Flühe', 'coordinates': FRANCE}


def test_entry_filter_without_city_matches_zip() -> None:
    assert cleanup.entry_filter(plan_row(cleanup.MOVE, city='')) == {'zip': '25899', 'coordinates': FRANCE}


def test_apply_row_updates_coordinates(geodata: MagicMock) -> None:
    geodata.update_many.return_value.modified_count = 2

    changed = cleanup.apply_row(plan_row(cleanup.UPDATE))

    assert changed == 2
    query, update = geodata.update_many.call_args.args
    assert query == {'zip': '25899', 'city': 'Flühe', 'coordinates': FRANCE}
    assert update == {'$set': {'coordinates': [54.75, 8.8]}}


def test_apply_row_moves_entry_to_not_found(geodata: MagicMock, not_found: MagicMock) -> None:
    geodata.delete_many.return_value.deleted_count = 1

    changed = cleanup.apply_row(plan_row(cleanup.MOVE))

    assert changed == 1
    assert geodata.delete_many.call_args.args[0] == {'zip': '25899', 'city': 'Flühe', 'coordinates': FRANCE}
    place, update = not_found.update_one.call_args.args
    assert place == {'zip': '25899', 'city': 'Flühe'}
    assert update['$setOnInsert']['reason'] == 'implausible: 790 km from zip centre (cleanup)'
    assert update['$setOnInsert']['rejected_coordinates'] == FRANCE


def test_apply_row_does_not_mark_not_found_when_entry_is_already_gone(geodata: MagicMock, not_found: MagicMock) -> None:
    geodata.delete_many.return_value.deleted_count = 0

    changed = cleanup.apply_row(plan_row(cleanup.MOVE))

    assert changed == 0
    not_found.update_one.assert_not_called()


def test_apply_row_rejects_unknown_action(geodata: MagicMock) -> None:
    row = plan_row('delete everything')

    with pytest.raises(ValueError):
        cleanup.apply_row(row)


def test_plan_command_writes_report_without_changing_geodata(
        geodata: MagicMock, not_found: MagicMock, search: FakeNominatimSearch, tmp_path: Path) -> None:
    geodata.find.return_value = [
        {'zip': '25899', 'city': 'Niebüll', 'coordinates': NIEBUELL},
        {'zip': '25899', 'city': 'Flühe', 'coordinates': FRANCE},
    ]
    report = tmp_path / 'plan.csv'

    cleanup.main(['plan', '--report', str(report)])

    assert [(r['city'], r['action']) for r in cleanup.read_plan(report)] == [('Flühe', cleanup.MOVE)]
    geodata.update_many.assert_not_called()
    geodata.delete_many.assert_not_called()
    not_found.update_one.assert_not_called()


def test_apply_command_executes_report(geodata: MagicMock, search: FakeNominatimSearch, tmp_path: Path) -> None:
    report = tmp_path / 'plan.csv'
    cleanup.write_plan(report, [plan_row(cleanup.UPDATE)])
    geodata.update_many.return_value.modified_count = 1

    cleanup.main(['apply', str(report)])

    geodata.update_many.assert_called_once()
    assert search.calls == []
