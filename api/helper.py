import datetime
from datetime import datetime
import time
import pymongo
import logging

MONGO_URI = 'mongodb://127.0.0.1:27017'
logging.basicConfig(filename='_phonebookdiver-api.log', level=logging.DEBUG)

def connect_db(page_str):
  try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client.phonebookdiver
  except pymongo.errors.ConnectionFailure as err:
    print(err)
  else:
    print(f'CONNECTED to {MONGO_URI} {db.name} | {page_str}')
    return db

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
    return convert_time(time_since)

def convert_time(time_value):
    if time_value >= 5400: return str(time_value/3600) + ' hours'
    elif time_value >= 180: return str(time_value/60) + ' minutes'
    return str(time_value) + ' seconds'

def get_all_collections(db):
  c = dict.fromkeys(db.list_collection_names(), 'name')
  ignore = ['geodata', 'geodata_anomalies', 'counties', 'states', 'zips_cities_counties_states']
  for i in ignore:
    if i in c:
      c.pop(i)
  return c
