import pymongo
from pymongo import MongoClient
from helper import log

# author: Mario Schuetz
#
# Provide database functionality
#

MONGO_URI = 'mongodb://mayo-nas:27017'

try:
  client = MongoClient(MONGO_URI)
  db = client.phonebookdiver 
except pymongo.errors.ConnectionFailure as err:
  log('LB', '')
  log('WARNING', str(err))
else:
  log('LB', '')
  info = 'CONNECTED to ' + MONGO_URI + ' ' + db.name
  log('INFO', info)

def get_database():
  return db

def get_collection(name):
    return db[name]

def insert_entry(entry, collection):
  c = get_collection(collection)
  try:
    c.insert_one(entry) 
  except pymongo.errors.DocumentTooLarge as err:
    log('WARNING', str(err))
    return 'FAILED'
  except pymongo.errors.OperationFailure as err:
    log('WARNING', str(err))
    return 'FAILED'
  else:
    return 'SUCCESS'

def insert_entries(entries, collection):
  c = get_collection(collection)
  try:
    c.insert_many(entries)
  except pymongo.errors.DocumentTooLarge as err:
    log('WARNING', str(err))
    return 'FAILED'
  except pymongo.errors.OperationFailure as err:
    log('WARNING', str(err))
    return 'FAILED'
  else:
    return 'SUCCESS'

def upsert_entry(id, entry, collection):
  c = get_collection(collection)
  try:
    c.update(id, entry, upsert=True)
  except pymongo.errors.DocumentTooLarge as err:
    log('WARNING', str(err))
    return 'FAILED'
  except pymongo.errors.OperationFailure as err:
    log('WARNING', str(err))
    return 'FAILED'
  else:
    return 'SUCCESS'
