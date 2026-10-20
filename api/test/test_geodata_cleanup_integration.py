from pathlib import Path

import pymongo
import pytest

from scripts import geodata_cleanup as cleanup
import hm_requester

# every test in this file talks to real services: Nominatim or the local MongoDB
pytestmark = pytest.mark.integration

GALMSBUELL = [54.7685346, 8.7919715]
NIEBUELL = [54.7868097, 8.8258359]
DAGEBUELL = [54.7306651, 8.7130636]
FRANCE = [47.8091066, 6.8970628]
BERLIN = [52.52, 13.405]
MARSOW = [53.4242109, 10.9311292]
VELLAHN = [53.3959, 10.9611]


class FakeNominatimSearch:
    """Zip centre for postcode-only queries; per-city answers for postcode + city queries."""

    def __init__(self) -> None:
        self.centres = {'25899': GALMSBUELL, '19260': MARSOW}
        self.cities = {}
        self.calls = 0

    def __call__(self, params: dict) -> list:
        self.calls += 1
        coords = self.cities.get(params['city']) if 'city' in params else self.centres.get(params['postalcode'])
        return [{'lat': str(coords[0]), 'lon': str(coords[1])}] if coords else []


@pytest.fixture
def search(monkeypatch: pytest.MonkeyPatch) -> FakeNominatimSearch:
    fake = FakeNominatimSearch()
    monkeypatch.setattr(hm_requester, 'nominatim_search', fake)
    return fake


@pytest.fixture
def geodata_with_wrong_entries(mongo_test_db: pymongo.database.Database) -> pymongo.database.Database:
    mongo_test_db['geodata'].insert_many([
        {'zip': '25899', 'city': 'Niebüll', 'area_code': '04661', 'coordinates': NIEBUELL},
        {'zip': '25899', 'city': 'Dagebüll', 'area_code': '04667', 'coordinates': DAGEBUELL},
        {'zip': '25899', 'city': 'Flühe', 'area_code': '04661', 'coordinates': FRANCE},
        {'zip': '25899', 'city': 'Flühe', 'area_code': '04662', 'coordinates': FRANCE},
        {'zip': '25899', 'city': 'Galmsbüll', 'area_code': '04667', 'coordinates': BERLIN},
        {'zip': '19260', 'city': 'Marsow', 'area_code': '038852', 'coordinates': MARSOW},
        {'zip': '19260', 'city': 'Vellahn', 'area_code': '038852', 'coordinates': VELLAHN},
        {'zip': '.....', 'city': 'Petershagen/Eggersdorf', 'area_code': '033439', 'coordinates': BERLIN},
    ])
    return mongo_test_db


def coords_of(db: pymongo.database.Database, zip: str, city: str) -> list:
    return [d['coordinates'] for d in db['geodata'].find({'zip': zip, 'city': city})]


def test_plan_finds_wrong_entries_and_changes_nothing(
        geodata_with_wrong_entries: pymongo.database.Database, search: FakeNominatimSearch, tmp_path: Path) -> None:
    search.cities = {'Galmsbüll': GALMSBUELL}
    before = list(geodata_with_wrong_entries['geodata'].find({}, {'_id': 0}))

    rows = cleanup.plan(str(tmp_path / 'plan.csv'))

    assert sorted((r['city'], r['action']) for r in rows) == [('Flühe', cleanup.MOVE), ('Galmsbüll', cleanup.UPDATE)]
    assert list(geodata_with_wrong_entries['geodata'].find({}, {'_id': 0})) == before
    assert geodata_with_wrong_entries[hm_requester.NOT_FOUND].count_documents({}) == 0


def test_plan_only_asks_about_suspect_zips(
        geodata_with_wrong_entries: pymongo.database.Database, search: FakeNominatimSearch, tmp_path: Path) -> None:
    search.cities = {'Galmsbüll': GALMSBUELL}

    cleanup.plan(str(tmp_path / 'plan.csv'))

    assert search.calls == 3  # centre of 25899, then Flühe and Galmsbüll; 19260 and '.....' untouched


def test_apply_fixes_and_moves_planned_entries(
        geodata_with_wrong_entries: pymongo.database.Database, search: FakeNominatimSearch, tmp_path: Path) -> None:
    db = geodata_with_wrong_entries
    search.cities = {'Galmsbüll': GALMSBUELL}
    report = str(tmp_path / 'plan.csv')
    cleanup.plan(report)

    changed = cleanup.apply(report)

    assert changed == 3  # Galmsbüll updated, both Flühe entries moved
    assert coords_of(db, '25899', 'Galmsbüll') == [GALMSBUELL]
    assert coords_of(db, '25899', 'Flühe') == []
    moved = db[hm_requester.NOT_FOUND].find_one({'zip': '25899', 'city': 'Flühe'})
    assert moved['rejected_coordinates'] == FRANCE
    assert moved['reason'].startswith('implausible: ') and moved['reason'].endswith(' km from zip centre (cleanup)')
    assert coords_of(db, '25899', 'Niebüll') == [NIEBUELL]
    assert coords_of(db, '19260', 'Vellahn') == [VELLAHN]
    assert coords_of(db, '.....', 'Petershagen/Eggersdorf') == [BERLIN]


def test_apply_twice_changes_nothing_more(
        geodata_with_wrong_entries: pymongo.database.Database, search: FakeNominatimSearch, tmp_path: Path) -> None:
    search.cities = {'Galmsbüll': GALMSBUELL}
    report = str(tmp_path / 'plan.csv')
    cleanup.plan(report)
    cleanup.apply(report)

    changed = cleanup.apply(report)

    assert changed == 0


def test_apply_leaves_entries_changed_since_planning_alone(
        geodata_with_wrong_entries: pymongo.database.Database, search: FakeNominatimSearch, tmp_path: Path) -> None:
    db = geodata_with_wrong_entries
    report = str(tmp_path / 'plan.csv')
    cleanup.plan(report)
    db['geodata'].update_many({'zip': '25899', 'city': 'Flühe'}, {'$set': {'coordinates': [54.8, 8.8]}})

    cleanup.apply(report)

    assert coords_of(db, '25899', 'Flühe') == [[54.8, 8.8], [54.8, 8.8]]
    assert db[hm_requester.NOT_FOUND].find_one({'city': 'Flühe'}) is None


def test_heatmap_does_not_request_moved_place_again(
        geodata_with_wrong_entries: pymongo.database.Database, search: FakeNominatimSearch, tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    db = geodata_with_wrong_entries
    report = str(tmp_path / 'plan.csv')
    cleanup.plan(report)
    cleanup.apply(report)
    db['2005_Q1'].insert_one({'lastname': 'Schütz', 'zip': '25899', 'city': 'Flühe', 'area_code': '04661'})
    monkeypatch.setattr(hm_requester.requests, 'get', lambda *a, **k: pytest.fail('unexpected Nominatim request'))

    positions = hm_requester.hm_query('2005_Q1', {'lastname': 'Schütz'})

    assert positions == []


def test_real_zip_centre_of_25899_is_galmsbuell(mongo_test_db: pymongo.database.Database) -> None:
    centre = cleanup.zip_centre('25899')

    assert centre == pytest.approx(GALMSBUELL, abs=0.05)


def test_real_regeocode_rejects_namesake_far_away(mongo_test_db: pymongo.database.Database) -> None:
    # Nominatim answers postcode 25899 + "Flühe" with a street in Oberstdorf, 87561
    centre = cleanup.zip_centre('25899')

    assert cleanup.regeocode('25899', 'Flühe', centre) is None


def test_real_regeocode_accepts_town_of_the_zip(mongo_test_db: pymongo.database.Database) -> None:
    centre = cleanup.zip_centre('25899')

    coords = cleanup.regeocode('25899', 'Niebüll', centre)

    assert hm_requester.distance_km(coords, NIEBUELL) < 5
