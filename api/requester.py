import pymongo
from pymongo import MongoClient
import requests

# author: Mario Schuetz
#
# Process api requests
#

MONGO_URI = 'mongodb://127.0.0.1:27017'

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

# used for heatmap
def find_entries(collection, key, value):
  print(f'Searching for {value} in {collection, key}')
  results = get_collection(collection).find(
    {key: value}, {'_id': 1, 'zip': 1, 'city': 1})
  print(f'Found {results.count()} results')
  if results is None:
    return []
  results = sort_results_by_zip_and_city(results)
  print('Geocoding')
  for r in results:
    zip = r.get('zip')
    city = r.get('city')
    r['coordinates']  = get_coords(zip, city)
  return results

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

def get_coords(zip, city):
  coords = db['zips_cities'].find_one({'zip': zip, 'city': city},  {'coordinates': 1})
  if coords is not None: return coords.get('coordinates')
  elif coords is  None:
    print(f'Requesting OSM API - {zip} {city}')
    # TODO when and where to update database?
    query_str = f'https://nominatim.openstreetmap.org/search.php?countrycode=de&q={zip}%20{city}&format=jsonv2'
    response = requests.get(query_str)
    response = response.json()

    if len(response) > 0:
      # return f'{float(response[0].get('lat'))} {float(response[0].get('lon'))}'
      return float(response[0].get('lat')), float(response[0].get('lon'))
  return None

# query over multiple collections - used for table view
def search_colls(start, end, key, value, seckey, secvalue):
  collections = get_all_collections()
  results = []
  query_msg = f'Querying the years from {start[:4]} to {end[:4]} for {key} = {value}'
  if seckey is not None and seckey != '' and secvalue is not None and secvalue != '':
    query_msg += f' and {seckey} = {secvalue}'
  print(query_msg)
  for c in collections:
    if c[:4] > end[:4]: continue
    if c[:4] < start[:4]: continue

    if seckey is not None and seckey != '' and secvalue is not None and secvalue != '':
      response = get_collection(c).find({key: value, seckey: secvalue})
    else:
      response = get_collection(c).find({key: value})
    
    
    if response.count() <= 0: continue
    # print(f'Found {response.count()} results in {c}')

    for resp in response:
      found = False
      resp_id = c + str(resp.get('_id'))
      ln = resp.get('lastname')
      if ln is None: ln = ''
      fn = resp.get('firstname')
      if fn is None: fn = ''
      zip = resp.get('zip')
      if zip is None: zip = ''
      city = resp.get('city')
      if city is None: city = ''
      st = resp.get('street')
      if st is None: st = ''
      stn = resp.get('street_number')
      if stn is None: stn = ''
      ac = resp.get('area_code')
      if ac is None: ac = ''

      # TODO: how to cope with same name at same address i.e. Michael Müller
      for res in results:
        res_ln = res.get('lastname')
        if res_ln is None: res_ln = ''
        res_fn = res.get('firstname')
        if res_fn is None: res_fn = ''
        res_zip = res.get('zip')
        if res_zip is None: res_zip = ''
        res_city = res.get('city')
        if res_city is None: res_city = ''
        res_st = res.get('street')
        if res_st is None: res_st = ''
        res_stn = res.get('street_number')
        if res_stn is None: res_stn = ''
        res_ac = res.get('area_code')
        if res_ac is None: res_ac = ''

        if ln == res_ln and fn == res_fn and zip == res_zip and city == res_city and st == res_st and stn.upper() == res_stn.upper() and ac == res_ac:
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
  return results

def add_coll_and_sort(list, item):
  list.append(item)
  return sorted(list)

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
