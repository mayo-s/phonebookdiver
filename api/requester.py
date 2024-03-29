import pymongo
import time
import requests
import collections
import helper

# author: Mario Schuetz
#
# Process api requests
#

db = helper.connect_db('Search')

def get_all_collections():
  return helper.get_all_collections(db)

# TODO Refactor - split into smaller pieces
# query over multiple collections - used for table view
# def search_colls(start, end, key, value, seckey, secvalue):
def search_colls(range, query_values):
  starttime = time.time()
  c_range = get_search_range(range[0], range[1])
  keys = list(query_values.keys())
  values = list(query_values.values())
  total_count = 0

  query_msg = f'Querying the phone books from {range[0]} to {range[1]} for\n{query_values}'
  print(query_msg)

  if range[0] == range[1]:

    results = list(db[range[0]].find(query_values))
    for res in results:
      res['edition'] = [range[0] + str(res.get('_id'))]
    print(f'Processing time {helper.processing_time(starttime, time.time())}')
    return results
  
  results = []
  # TODO refactor - minimze loops
  for c in c_range:

    response = db[c].find(query_values)
    if response.count() <= 0: continue
    # print(f'Found {response.count()} results in {c}')
    total_count += response.count()
    for resp in response:
      found = False
      resp_id = c + str(resp.get('_id'))
      resp_hash = build_address_hash(collections.OrderedDict(sorted(resp.items())))
      for res in results:
        res_hash = build_address_hash(collections.OrderedDict(sorted(res.items())))
        
        if resp_hash == res_hash:
          res['edition'] = add_coll_and_sort(res['edition'], resp_id)
          res = merge_dict_results(res, resp)
          found = True
          break
      if not found:
        new_result = resp
        new_result['edition'] = []
        new_result['_id'] = resp_id
        new_result['edition'].append(resp_id)
        results.append(new_result)

  print(f'Found {str(total_count)} total results. Returned {len(results)}')
  print(f'Processing time {helper.processing_time(starttime, time.time())}')
  return results

def build_address_hash(address):
  wanted_keys = ['lastname', 'firstname', 'zip', 'city', 'street', 'street_number', 'area_code', 'phonenumber']
  address_str = ''
  for k in address:
    if k in wanted_keys:
      address_str += address.get(k)
      if k == 'street_number':
        address_str = address_str.replace(' ', '')
      if k == 'street':
        address_str = replace_dash_str(address_str)
  return address_str.lower().__hash__()

def add_coll_and_sort(list, item):
  list.append(item)
  return sorted(list)

def get_search_range(start, end):
  all_collections = get_all_collections()
  range = []
  for c in all_collections:

    if c[:4] > end[:4]: continue
    elif c[:4] == end[:4] and c[6:] > end[6:]: continue
    elif c[:4] < start[:4]: continue 
    elif c[:4] == start[:4] and c[6:] < start[6:]: continue

    range.append(c)
  return range

def merge_dict_results(dict1, dict2):
  ignore_list = ['_id', 'street_index', 'street_index_hnr', 'coordinates']

  for elem2 in dict2:
    if elem2 in ignore_list: continue
    elem2_value = dict2.get(elem2)
    if elem2 == 'street':
      elem2_value = replace_dash_str(elem2_value)
      dict1[elem2] = elem2_value
      continue
    if elem2 not in dict1:
      dict1[elem2] = elem2_value
    elif dict1[elem2].lower() == elem2_value.lower():
      continue
  return dict1

def replace_dash_str(street_str):
  if street_str[(len(street_str)-1):] == '-':
    return street_str[:(len(street_str)-1)] + 'str.'
  return street_str
      

def fetch_details_by_id(_id):
  return db[_id[:7]].find_one({'_id': int(_id[7:])})

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
