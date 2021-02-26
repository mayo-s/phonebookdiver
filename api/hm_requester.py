import pymongo
from pymongo import MongoClient
import time
import requests
import helper

# author: Mario Schuetz
#
# Process heatmap requests
#
db = None

def hm_set_db(database):
  global db 
  db = database

# used for heatmap
def hm_query(collection, query):
  start = time.time()
  print(f'Searching for {query} in {collection}')
  results = db[collection].find(query, {'_id': 1, 'zip': 1, 'city': 1, 'area_code':1})
  print(f'Found {results.count()} results')
  if results is None:
    return []
  results = sort_results_by_zip_and_city(results)
  print('Geocoding...')
  geo_list = []
  for r in results:
    zip = r.get('zip')
    city = r.get('city')
    area_code = r.get('area_code')
    if zip is None and city is None: continue
    # TODO add count to coords
    coords = get_coords(zip, city, area_code)
    if coords is None: 
      continue
    coords.append(r.get('count'))
    geo_list.append(coords)
  print(f'Returning {len(geo_list)} positions')
  print(f'Processing time {helper.processing_time(start, time.time())}')
  return geo_list

def sort_results_by_zip_and_city(results):
  print('Sorting...')
  sorted_results = []
  for r in results:
    zip = r.get('zip')
    city = r.get('city')
    area_code = r.get('area_code')
    address = f'{zip} {city} Deutschland'
    found = False
    for sr in sorted_results:
      if address == sr.get('address'):
        sr['count'] = sr.get('count') + 1
        found = True
        break
    if not found: sorted_results.append({'address': address, 'zip': zip, 'city': city, 'area_code': area_code, 'count': 1})

  return sorted_results

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
  coords = db['geodata'].find_one(query,  {'coordinates': 1})
  if coords is not None: return coords.get('coordinates')
  else:
    if zip is None: zip = ''
    if city is None: city = ''
    query_str = f'https://nominatim.openstreetmap.org/search.php?countrycode=de&q={zip}%20{city}%20Deutschland&format=jsonv2'
    response = requests.get(query_str)
    response = response.json()

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
      if api_coords is not None:
        update_coords_collection(zip, city, area_code, api_coords)
        return api_coords
      print(f'None {zip} {city}')

  return None
