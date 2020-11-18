import pymongo
from pymongo import MongoClient
import requests
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from operator import itemgetter

geolocator = Nominatim(user_agent="phonebookdiver")

# author: Mario Schuetz
#
# Process api requests
#

MONGO_URI = 'mongodb://mayo-nas:27017'

try:
  client = MongoClient(MONGO_URI)
  db = client.phonebookdiver
except pymongo.errors.ConnectionFailure as err:
  print(err)
else:
  print(f'CONNECTED to {MONGO_URI} {db.name}')

def get_collection(name):
  return db[name]


def get_all_collections():
  return dict.fromkeys(db.list_collection_names(), 'name')


def find_entries(collection, key, value):
  print(f'Searching for {value} in {collection, key}')
  results = get_collection(collection).find(
    {key: value}, {'_id': 1, 'zip': 1, 'city': 1})
  print(f'Found {results.count()} results')
  if results is None:
    return []
  results = sort_results_by_zip_and_city(results)
  # geo_list = []
  # for result in results:
  #   geo_list.append(geocoding_single(result))
  geo_list = geocoding_bulk(results)
  return geo_list


def sort_results_by_zip_and_city(results):
  print('Sorting...')
  sorted_results = []
  for r in results:
    zip = r.get('zip')
    city = r.get('city')
    address = f'{zip} {city} Germany'
    found = False
    for sr in sorted_results:
      if address == sr.get('address'):
        sr['count'] = sr.get('count') + 1
        found = True
        break
    if not found: sorted_results.append({'address': address, 'count': 1})

  return sorted_results

def geocoding_single(address):
  print('GeoCoding...')
  query_str = f'https://nominatim.openstreetmap.org/search.php?countrycode=de&q={address.get("address")}&format=jsonv2'
  # print(f'\n{address}\n{query_str}\n')
  response = requests.get(query_str)
  response = response.json()

  # print test data / API use only
  # if len(response) > 0:
  #   address['lat'] = float(response[0].get('lat'))
  #   address['lng'] = float(response[0].get('lon'))
  #   return address

  if len(response) > 0:
    return [float(response[0].get('lat')), float(response[0].get('lon')), address.get('count')]
  return []

def geocoding_bulk(addresses):
  print('GeoCoding...')
  geolocator = Nominatim(user_agent='phonebookdiver')

  geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
  locations = [geocode(a.get('address')) for a in addresses]

  coords = []
  cnt_no_coords = 0
  for l in locations:
    try:
      coords.append([l.latitude, l.longitude])
    except AttributeError: cnt_no_coords +=1 

  print(f'... {cnt_no_coords} with missing lat/lng')
  return coords

def search_colls(start, end, key, value):
  collections = get_all_collections()
  results = []
  print(f'Querying the years from {start[:4]} to {end[:4]} for {key} = {value}')
  for c in collections:
    if c[:4] > end[:4]: continue
    if c[:4] < start[:4]: continue

    response = get_collection(c).find({key: value}, {'firstname': 1, 'lastname': 1, 'zip': 1, 'city': 1, 'street': 1, 'street_number': 1, 'area_code': 1, 'phonenumber': 1})
    if response.count() <= 0: continue
    # print(f'Found {response.count()} results in {c}')
    
    for r in response:
      found = False
      ln = r.get('lastname')
      fn = r.get('firstname')
      zip = r.get('zip')
      city = r.get('city')
      st = r.get('street')
      stn = r.get('street_number')

      # TODO: how to cope with same name at same address i.e. Michael Müller
      for res in results:
        if key == 'lastname':
          if fn == res.get('firstname') and zip == res.get('zip') and city == res.get('city'):
            res['appearance'] = add_item_and_sort(res['appearance'], c)
            found = True
            break
        if key == 'firstname':
          if ln == res.get('lastname') and zip == res.get('zip') and city == res.get('city'):
            res['appearance'] = add_item_and_sort(res['appearance'], c)
            found = True
            break

      if not found:
        new_result = r
        new_result['appearance'] = []
        new_result['appearance'].append(c)
        new_result['_id'] = c + str(r.get('_id'))
        results.append(new_result)
  print(f'Found {len(results)} total results')
  return results

def add_item_and_sort(list, item):
  list.append(item)
  return sorted(list)
