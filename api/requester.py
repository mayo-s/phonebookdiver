import pymongo
from pymongo import MongoClient
import datetime
from datetime import datetime
import time
import logging
import requests

# author: Mario Schuetz
#
# Process api requests
#

logging.basicConfig(filename='_phonebookdiver-OSM-requests.log', level=logging.DEBUG)
MONGO_URI = 'mongodb://127.0.0.1:27017'

try:
  client = MongoClient(MONGO_URI)
  db = client.phonebookdiver
except pymongo.errors.ConnectionFailure as err:
  print(err)
else:
  print(f'CONNECTED to {MONGO_URI} {db.name}')

def log(type, msg):
  date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
  msg = ' ' + date_time + ' ' + msg
  if type == 'WARNING':
    logging.warning(msg)
  if type == 'INFO':
    logging.info(msg)
  if type == 'LB':
    logging.info('')

def processing_time(start, end):
    time_since = end - start
    return str(time_since) + ' seconds'

def get_collection(name):
  return db[name]


def get_all_collections():
  c = dict.fromkeys(db.list_collection_names(), 'name')
  ignore = ['geodata', 'counties', 'states', 'zips_cities_counties_states']
  for i in ignore:
    if i in c:
      c.pop(i)
  return c

# used for heatmap
def find_entries(collection, key, value):
  start = time.time()
  print(f'Searching for {value} in {collection, key}')
  results = get_collection(collection).find(
    {key: value}, {'_id': 1, 'zip': 1, 'city': 1})
  print(f'Found {results.count()} results')
  if results is None:
    return []
  results = sort_results_by_zip_and_city(results)
  print('Geocoding...')
  geo_list = []
  for r in results:
    zip = r.get('zip')
    city = r.get('city')
    if zip is None and city is None: continue
    # TODO add count to coords
    coords = get_coords(zip, city)
    if coords is None: 
      continue
    coords.append(r.get('count'))
    geo_list.append(coords)
  print(f'Returning {len(geo_list)} positions')
  print(f'Processing time {processing_time(start, time.time())}')
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
    if not found: sorted_results.append({'address': address, 'zip': zip, 'city': city, 'count': 1})

  return sorted_results

def update_coords_collection(zip, city, coords):
  msg = f'Requesting OSM API - {zip} {city} {coords}'
  log('INFO', msg)
  print(msg)
  db['geodata'].insert_one({'zip': zip, 'city':city, 'coordinates':coords})

def get_coords(zip, city):
  query = {'zip': zip, 'city': city}
  if zip is None: query = {'city': city}
  if city is None: query = {'zip': zip}
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
        update_coords_collection(zip, city, api_coords)
        return api_coords
      print(f'None {zip} {city}')

  return None

# TODO Refactor - split into smaller pieces
# query over multiple collections - used for table view
# def search_colls(start, end, key, value, seckey, secvalue):
def search_colls(range, query_values):
  starttime = time.time()
  c_range = get_search_range(range[0], range[1])
  keys = list(query_values.keys())
  values = list(query_values.values())

  query_msg = f'Querying the phone books from {range[0]} to {range[1]} for\n{query_values}'
  print(query_msg)
  
  results = []
  for c in c_range:

    response = get_collection(c).find(query_values)
    if response.count() <= 0: continue
    # print(f'Found {response.count()} results in {c}')

    for resp in response:
      found = False
      resp_id = c + str(resp.get('_id'))
      ln, fn, zip, city, st, stn, ac = '', '', '', '', '', '', ''
      if resp.get('lastname') is not None: ln = resp.get('lastname')
      if resp.get('firstname') is not None: fn = resp.get('firstname')
      if resp.get('zip') is not  None: zip = resp.get('zip')
      if resp.get('city') is not None: city = resp.get('city')
      if resp.get('street') is not None: st = resp.get('street')
      if resp.get('street_number') is not None: stn = resp.get('street_number')
      if resp.get('area_code') is not None: ac = resp.get('area_code')

      # TODO: how to cope with same name at same address i.e. Michael Müller
      for res in results:
        res_ln, res_fn, res_zip, res_city, res_st, res_stn, res_ac = '', '', '', '', '', '', ''
        if res.get('lastname') is not None: res_ln = res.get('lastname')
        if res.get('firstname') is not None: res_fn = res.get('firstname')
        if res.get('zip') is not  None: res_zip = res.get('zip')
        if res.get('city') is not None: res_city = res.get('city')
        if res.get('street') is not None: res_st = res.get('street')
        if res.get('street_number') is not None: res_stn = res.get('street_number')
        if res.get('area_code') is not None: res_ac = res.get('area_code')
        

        if ln.lower() == res_ln.lower() and fn.lower() == res_fn.lower() and zip == res_zip and city.lower() == res_city.lower() and st.lower() == res_st.lower() and stn.upper() == res_stn.upper() and ac.lower() == res_ac.lower():
          res['appearance'] = add_coll_and_sort(res['appearance'], resp_id)
          temp_res = merge_dict_results(res, resp)
          if temp_res is None: break
          else:
            res = temp_res
            found = True
            break

      if not found:
        new_result = resp
        new_result['appearance'] = []
        new_result['_id'] = resp_id
        new_result['appearance'].append(resp_id)
        results.append(new_result)

  print(f'Found {len(results)} total results')
  print(f'Processing time {processing_time(starttime, time.time())}')
  return results

def add_coll_and_sort(list, item):
  list.append(item)
  return sorted(list)

def get_search_range(start, end):
  all_collections = get_all_collections()
  range = []
  for c in all_collections:

    if int(c[:4]) > int(end[:4]): continue
    elif int(c[:4]) == int(end[:4]) and int(c[6:]) > int(end[6:]): continue
    elif c[:4] < start[:4]: continue 
    elif c[:4] == start[:4] and int(c[6:]) < int(end[6:]): continue

    range.append(c)

  return range

def merge_dict_results(dict1, dict2):
  ignore_list = ['_id', 'street_index', 'street_index_hnr', 'coordinates']

  for elem2 in dict2:
    if elem2 in ignore_list: continue
    if elem2 not in dict1:
      dict1[elem2] = dict2.get(elem2)
    elif dict1[elem2].lower() == dict2.get(elem2).lower():
      continue
    else: 
      return None

  return dict1

def fetch_details_by_id(_id):
  return get_collection(_id[:7]).find_one({'_id': int(_id[7:])})

def get_federal_states():
  response = db['states'].find({})
  states = []
  for r in response:
    states.append(r['state'])
  return states

def get_counties():
  response = db['counties'].find({})
  counties = []
  for r in response:
    counties.append(r['county'])
  return counties
