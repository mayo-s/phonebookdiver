import pymongo
from pymongo import MongoClient
import requests

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

# def get_database():
#   return db


def get_collection(name):
  return db[name]


def get_all_collections():
  return dict.fromkeys(db.list_collection_names(), 'name')


def count_lastnames(value):
  try:
    result = get_collection('1998_Q3').count_documents(
      {'lastname': {'$regex': value}})
  except pymongo.errors.OperationFailure as err:
    print(str(err))
    return 'FAILED'
  else:
    return str(result)


def find_entries(collection, key, value):
  print(f'Searching for {value} in {collection, key}')
  results = get_collection(collection).find(
    {key: value}, {'_id': 1, 'zip': 1, 'city': 1})
  print(f'Found {results.count()} results')
  if results is None:
    return []
  results = sort_results_by_zip_and_city(results)
  list = []
  for result in results:
    # TODO check if database lat-lng is None/Empty before geocoding
    # if so - UPDATE database after geocoding
    # print(result)
    # if result.get('lat') is not None and result.get('lng') is not None:
    #   list.append([result.get('lat'), result.get('lng')])
    # else:
    list.append(geocoding(result))
  return list


def sort_results_by_zip_and_city(results):
  sorted_results = []
  for r in results:
    zip = r.get('zip')
    city = r.get('city')
    found = False
    for sr in sorted_results:
      if zip == sr.get('zip') and city == sr.get('city'):
        sr['count'] = sr.get('count') + 1
        found = True
        break
    if not found: sorted_results.append({'zip': zip, 'city': city, 'count': 1})

  return sorted_results

def geocoding(address):
  zip = ''
  city = ''
  street = ''
  street_nr = ''
  if address.get('zip') is not None:
    zip = f'{address.get("zip")}%20'
  if address.get('city') is not None:
    city = f'{address.get("city")}%2C%20'
  if address.get('street') is not None:
    street = f'{address.get("street")}'
    if street[len(street) - 1] is '-':
      street = ''.join([street[:len(street) - 1], 'strasse'])
    address['street'] = street
    street = f'{street}%20'
  if address.get('street_number') is not None:
    street_nr = f'{address.get("street_number")}'

  query_str = f'https://nominatim.openstreetmap.org/search.php?countrycode=de&q={zip}{city}{street}{street_nr}&format=jsonv2'
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
