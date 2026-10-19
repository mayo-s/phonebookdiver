import sys
import threading
import pymongo
import time
import requests
import helper

db = helper.connect_db('Heatmap')
# Nominatim usage policy requires an identifying User-Agent with contact info
NOMINATIM_HEADERS = {'User-Agent': 'phonebookdiver/1.0 (https://github.com/mayo-s/phonebookdiver)'}
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search.php'
NOMINATIM_TIMEOUT = 10  # seconds
# Nominatim usage policy allows at most one request per second
NOMINATIM_MIN_INTERVAL = 1.0  # seconds
last_nominatim_request = 0.0
nominatim_lock = threading.Lock()  # flask serves requests in parallel threads


def ensure_geodata_indexes() -> None:
    try:
        db['geodata'].create_index([('zip', pymongo.ASCENDING), ('city', pymongo.ASCENDING)])
        db['geodata'].create_index('area_code')
    except pymongo.errors.PyMongoError as err:
        msg = f'Could not create geodata indexes, heatmap lookups will be slow: {err}'
        helper.log('WARNING', msg)
        print(msg)


# used for heatmap
def hm_query(collection, query):
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


def update_coords_collection(zip, city, area_code, coords):
    insert_obj = {}
    if zip: insert_obj['zip'] = zip
    if city: insert_obj['city'] = city
    if area_code: insert_obj['area_code'] = area_code
    if coords: insert_obj['coordinates'] = coords
    msg = f'Insert into geodata {insert_obj}'
    helper.log('INFO', msg)
    print(msg)
    db['geodata'].insert_one(insert_obj)


def get_coords(zip, city, area_code):
    query = {}
    if zip: query['zip'] = zip
    if city: query['city'] = city
    coords = db['geodata'].find_one(query, {'coordinates': 1})
    if coords:
        return coords.get('coordinates')
    else:
        # TODO double checked?
        if zip is None: return None
        if city is None: city = ''
        response = request_nominatim(zip, city)

        # TODO double check if values in bounds of Germany
        # North: 55.0583° N, 8.4165° E  (> 55.1)
        # South: 47.2701° N, 10.1783° E (< 47.2)
        # East: 51.2729° N, 15.0419° E  (> 15.1)
        # West: 51.0511° N, 5.8663° E   (< 5.8)

        if len(response) > 0:
            # return f'{float(response[0].get('lat'))} {float(response[0].get('lon'))}'
            api_coords = [float(response[0].get('lat')), float(response[0].get('lon'))]

            if api_coords != api_coords:
                print(f'NaN {zip} {city}')
                return None
            if api_coords:
                if valid_area_code(area_code):
                    update_coords_collection(zip, city, area_code, api_coords)
                return api_coords
            print(f'None {zip} {city}')

    return None


def wait_for_nominatim_slot() -> None:
    global last_nominatim_request
    with nominatim_lock:
        wait = NOMINATIM_MIN_INTERVAL - (time.monotonic() - last_nominatim_request)
        if wait > 0:
            time.sleep(wait)
        last_nominatim_request = time.monotonic()


def request_nominatim(zip: str, city: str) -> list:
    """Returns [] on any failure, so one unresolved place doesn't break the whole heatmap."""
    wait_for_nominatim_slot()
    query_str = f'{NOMINATIM_URL}?countrycode=de&q={zip}%20{city}%20Deutschland&format=jsonv2'
    try:
        response = requests.get(query_str, headers=NOMINATIM_HEADERS, timeout=NOMINATIM_TIMEOUT)
        response.raise_for_status()
        results = response.json()
    except requests.RequestException as err:
        msg = f'Nominatim request failed for {zip} {city}: {err}'
        helper.log('WARNING', msg)
        print(msg)
        return []
    if not isinstance(results, list):
        msg = f'Unexpected Nominatim response for {zip} {city}: {results}'
        helper.log('WARNING', msg)
        print(msg)
        return []
    return results


def get_coords_by_area_code(area_code):
    coords = db['geodata'].find_one({'area_code': area_code}, {'coordinates': 1})
    if coords:
        return coords.get('coordinates')
    return None


def valid_area_code(area_code):
    ignore = ['0310', '0311', '032', '0700', '0701', '0800', '0801', '0900', '09001', '09002', '09003', '09004',
              '09005']
    if area_code is None:
        return False
    elif area_code in ignore:
        return False
    elif area_code[:2] == '01':
        return False
    return True
