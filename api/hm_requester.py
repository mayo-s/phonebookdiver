import math
import threading
import time
from datetime import datetime, timezone

import helper
import pymongo
import requests

db = helper.connect_db('Heatmap')
# Nominatim usage policy requires an identifying User-Agent with contact info
NOMINATIM_HEADERS = {'User-Agent': 'phonebookdiver/1.0 (https://github.com/mayo-s/phonebookdiver)'}
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search.php'
NOMINATIM_TIMEOUT = 10  # seconds
# Nominatim usage policy allows at most one request per second
NOMINATIM_MIN_INTERVAL = 1.0  # seconds
last_nominatim_request = 0.0
nominatim_lock = threading.Lock()  # flask serves requests in parallel threads
NOT_FOUND = 'geodata_not_found'
MAX_KM_TO_SAME_ZIP = 35
GERMANY_LAT = (47.2, 55.1)
GERMANY_LON = (5.8, 15.1)
EARTH_RADIUS_KM = 6371


def ensure_geodata_indexes() -> None:
    try:
        db['geodata'].create_index([('zip', pymongo.ASCENDING), ('city', pymongo.ASCENDING)])
        db['geodata'].create_index('area_code')
        db[NOT_FOUND].create_index([('zip', pymongo.ASCENDING), ('city', pymongo.ASCENDING)], unique=True)
    except pymongo.errors.PyMongoError as err:
        msg = f'Could not create geodata indexes, heatmap lookups will be slow: {err}'
        helper.log('WARNING', msg)
        print(msg)


# used for heatmap
def hm_query(collection: str, query: dict) -> list:
    start = time.time()
    print(f'Searching for {query} in {collection}')
    results = find_places(collection, query)
    if not results:
        print('Found 0 results')
        return []
    print(f'Found {sum(r.get("count") for r in results)} results in {len(results)} places')
    print('Geocoding...')
    cache = load_geodata_cache(results)
    geo_list = []
    for r in results:
        coords = locate_place(r, cache)
        if coords is None:
            continue
        # new list, so the count never ends up in the cached coordinates
        geo_list.append(coords + [r.get('count')])
    print(f'Returning {len(geo_list)} positions')
    print(f'Processing time {helper.processing_time(start, time.time())}')
    return geo_list


def find_places(collection: str, query: dict) -> list:
    pipeline = [
        {'$match': query},
        {'$group': {
            '_id': {
                'zip': {'$toLower': '$zip'},
                'city': {'$toLower': '$city'},
                'area_code': {'$toLower': '$area_code'},
            },
            'zip': {'$first': '$zip'},
            'city': {'$first': '$city'},
            'area_code': {'$first': {'$ifNull': ['$area_code', '']}},
            'count': {'$sum': 1},
        }},
        {'$project': {'_id': 0}},
    ]
    return list(db[collection].aggregate(pipeline, allowDiskUse=True))


def load_geodata_cache(places: list) -> dict:
    zips = set()
    area_codes = set()
    for p in places:
        if p.get('zip'):
            zips.add(p.get('zip'))
        elif valid_area_code(p.get('area_code')):
            area_codes.add(p.get('area_code'))
    return {'places': load_cached_places(zips), 'area_codes': load_cached_area_codes(area_codes)}


def load_cached_places(zips: set) -> dict:
    places = {}
    if not zips:
        return places
    for doc in db['geodata'].find({'zip': {'$in': list(zips)}}, {'_id': 0, 'zip': 1, 'city': 1, 'coordinates': 1}):
        places.setdefault((doc.get('zip'), doc.get('city')), doc.get('coordinates'))
        places.setdefault((doc.get('zip'), None), doc.get('coordinates'))
    for doc in db[NOT_FOUND].find({'zip': {'$in': list(zips)}}, {'_id': 0, 'zip': 1, 'city': 1}):
        places.setdefault((doc.get('zip'), doc.get('city')), None)
    return places


def load_cached_area_codes(area_codes: set) -> dict:
    coords = {}
    if not area_codes:
        return coords
    for doc in db['geodata'].find({'area_code': {'$in': list(area_codes)}},
                                  {'_id': 0, 'area_code': 1, 'coordinates': 1}):
        coords.setdefault(doc.get('area_code'), doc.get('coordinates'))
    return coords


def locate_place(place: dict, cache: dict) -> list | None:
    """Caches get_coords results too, so each zip + city is looked up only once per search."""
    zip = place.get('zip')
    city = place.get('city')
    area_code = place.get('area_code')
    if zip:
        key = (zip, city or None)
        if key not in cache['places']:
            cache['places'][key] = get_coords(zip, city, area_code)
        return cache['places'][key]
    if valid_area_code(area_code):
        return cache['area_codes'].get(area_code)
    return None


def place_query(zip: str, city: str | None) -> dict:
    query = {'zip': zip}
    if city:
        query['city'] = city
    return query


def save_coords(zip: str, city: str | None, area_code: str | None, coords: list) -> None:
    """One entry per zip + city. The area code is only stored if valid, so mobile prefixes never get a location."""
    place = place_query(zip, city)
    new_fields = {'coordinates': coords}
    if valid_area_code(area_code):
        new_fields['area_code'] = area_code
    upsert_place('geodata', place, new_fields)


def save_not_found(zip: str, city: str | None, reason: str = 'unknown to Nominatim',
                   rejected: list | None = None) -> None:
    fields = {'checked': datetime.now(timezone.utc), 'reason': reason}
    if rejected:
        fields['rejected_coordinates'] = rejected
    upsert_place(NOT_FOUND, place_query(zip, city), fields)


def upsert_place(collection: str, place: dict, new_fields: dict) -> None:
    try:
        db[collection].update_one(place, {'$setOnInsert': new_fields}, upsert=True)
    except pymongo.errors.PyMongoError as err:
        msg = f'Could not save {place} to {collection}: {err}'
        helper.log('WARNING', msg)
        print(msg)
        return
    helper.log('INFO', f'Saved to {collection} {place} {new_fields}')


def parse_nominatim_coords(results: list) -> list | None:
    if not results:
        return None
    try:
        coords = [float(results[0].get('lat')), float(results[0].get('lon'))]
    except (TypeError, ValueError, AttributeError):
        return None
    if any(math.isnan(c) for c in coords):
        return None
    return coords


def distance_km(a: list, b: list) -> float:
    """Great-circle (haversine) distance between two [lat, lon] points."""
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))


def in_germany(coords: list) -> bool:
    return GERMANY_LAT[0] <= coords[0] <= GERMANY_LAT[1] and GERMANY_LON[0] <= coords[1] <= GERMANY_LON[1]


def is_postcode(zip: str) -> bool:
    return zip.isdigit() and len(zip) == 5


def implausibility(zip: str, coords: list) -> str | None:
    """Why coords can't belong to this zip, or None."""
    if not in_germany(coords):
        return 'outside Germany'
    nearest = nearest_same_zip_km(zip, coords)
    if nearest is not None and nearest > MAX_KM_TO_SAME_ZIP:
        return f'{nearest:.0f} km from the nearest place with zip {zip}'
    return None


def nearest_same_zip_km(zip: str, coords: list) -> float | None:
    """Distance to the nearest cached place with this zip, None if there is none or zip is a placeholder.

    Nearest, not an average, so a few wrongly geocoded old entries can't get a correct result rejected.
    """
    if not is_postcode(zip):
        return None
    neighbours = [d['coordinates'] for d in db['geodata'].find({'zip': zip}, {'_id': 0, 'coordinates': 1})
                  if d.get('coordinates')]
    return min((distance_km(coords, n) for n in neighbours), default=None)


def get_coords(zip: str | None, city: str | None, area_code: str | None) -> list | None:
    # TODO double checked?
    if not zip:
        return None
    cached = db['geodata'].find_one(place_query(zip, city), {'coordinates': 1})
    if cached:
        return cached.get('coordinates')
    if db[NOT_FOUND].find_one(place_query(zip, city), {'_id': 1}):
        return None
    return resolve_with_nominatim(zip, city, area_code)


def resolve_with_nominatim(zip: str, city: str | None, area_code: str | None) -> list | None:
    results = request_nominatim(zip, city or '')
    if results is None:
        return None
    coords = parse_nominatim_coords(results)
    if coords is None:
        print(f'None {zip} {city}')
        save_not_found(zip, city)
        return None
    reason = implausibility(zip, coords)
    if reason:
        msg = f'Rejected Nominatim result {coords} for {zip} {city}: {reason}'
        helper.log('WARNING', msg)
        print(msg)
        save_not_found(zip, city, reason=f'implausible: {reason}', rejected=coords)
        return None
    save_coords(zip, city, area_code, coords)
    return coords


def wait_for_nominatim_slot() -> None:
    global last_nominatim_request
    with nominatim_lock:
        wait = NOMINATIM_MIN_INTERVAL - (time.monotonic() - last_nominatim_request)
        if wait > 0:
            time.sleep(wait)
        last_nominatim_request = time.monotonic()


def request_nominatim(zip: str, city: str) -> list | None:
    return nominatim_search({'countrycode': 'de', 'q': f'{zip} {city} Deutschland', 'format': 'jsonv2'})


def nominatim_search(params: dict) -> list | None:
    """Returns None on failure and [] if Nominatim knows no such place; only the latter is worth remembering."""
    wait_for_nominatim_slot()
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=NOMINATIM_HEADERS, timeout=NOMINATIM_TIMEOUT)
        response.raise_for_status()
        results = response.json()
    except requests.RequestException as err:
        msg = f'Nominatim request failed for {params}: {err}'
        helper.log('WARNING', msg)
        print(msg)
        return None
    if not isinstance(results, list):
        msg = f'Unexpected Nominatim response for {params}: {results}'
        helper.log('WARNING', msg)
        print(msg)
        return None
    return results


def get_coords_by_area_code(area_code: str) -> list | None:
    coords = db['geodata'].find_one({'area_code': area_code}, {'coordinates': 1})
    if coords:
        return coords.get('coordinates')
    return None


def valid_area_code(area_code: str | None) -> bool:
    ignore = ['0310', '0311', '032', '0700', '0701', '0800', '0801', '0900', '09001', '09002', '09003', '09004',
              '09005']
    if not area_code:
        return False
    elif area_code in ignore:
        return False
    elif area_code[:2] == '01':
        return False
    return True
