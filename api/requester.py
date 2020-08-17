import pymongo
from pymongo import MongoClient
import requests
# from .tools.data_cleaner import check_substring

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
    result = get_collection('1998_Q3').count_documents({'lastname': {'$regex': value}})
  except pymongo.errors.OperationFailure as err:
    print(str(err))
    return 'FAILED'
  else:
    return str(result)

def find_entries(collection, key, value):
  value = revert_spec_chars(value)
  # print(f'Searching for {value} in {collection, key}')
  results = get_collection(collection).find({key: value}, { '_id': 1, 'street': 1, 'street_number': 1, 'zip': 1, 'city': 1 })
  if results is None:
    return 'NO MATCH FOUND'
  list = []
  for result in results:
    list.append(geocoding(result))
  return list

def geocoding(address):
  zip = ''
  city = ''
  street = ''
  street_nr = ''
  if address.get('zip') is not None:
    zip = f'{address.get("zip")}%20'

  if address.get('city') is not None:
    city = f'{address.get("city")}'
    # TODO can be removed when all data is clean
    city = spec_chars(city)
    address['city'] = city
    city = f'{city}%2C%20'
  if address.get('street') is not None:
    street = f'{address.get("street")}'
    # TODO can be removed when all data is clean
    street = spec_chars(street)
    if street[len(street) - 1] is '-':
      street = ''.join([street[:len(street) - 1], 'strasse'])
    address['street'] = street
    street = f'{street}%20'
  if address.get('street_number') is not None:
    street_nr = f'{address.get("street_number")}'

  query_str= f'https://nominatim.openstreetmap.org/search.php?countrycode=de&q={zip}{city}{street}{street_nr}&format=jsonv2'
  # print(f'\n{address}\n{query_str}\n')
  response = requests.get(query_str)
  # print(response.status_code)
  # print(response.text)
  response = response.json()
  coords = {
    'lat': '',
    'lng': ''
  }
  if len(response) > 0:
    # address['lat'] = response[0].get('lat')
    # address['lng'] = response[0].get('lon')
    coords['lat'] = response[0].get('lat')
    coords['lng'] = response[0].get('lon')    
  return coords

def spec_chars(str):
  special_chars = {
    'ΓöÇ': 'Ä',
    '╬ú': 'ä',
    'Γòô': 'Ö',
    '├╖': 'ö',
    'Γûä': 'Ü',
    'Γü┐': 'ü',
    'ΓûÇ': 'ß',
  }
  for sc in special_chars:
    str = str.replace(sc, special_chars.get(sc))
  return str

def revert_spec_chars(str):
  special_chars = {
    'Ä': 'ΓöÇ' ,
    'ä': '╬ú',
    'Ö': 'Γòô',
    'ö': '├╖',
    'Ü': 'Γûä',
    'ü': 'Γü┐',
    'ß': 'ΓûÇ',
  }
  for sc in special_chars:
    str = str.replace(sc, special_chars.get(sc))
  return str
