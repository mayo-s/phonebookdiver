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

def get_all_collections():
  return dict.fromkeys(db.list_collection_names(), 'name')

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

def update_doc(collection, id, key, value):
  c = get_collection(collection)
  try:
    c.update_one({'_id': id}, {'$set': {key: value}})
  except pymongo.errors.DocumentTooLarge as err:
    log('WARNING', str(err))
    return 'FAILED'
  except pymongo.errors.OperationFailure as err:
    log('WARNING', str(err))
    return 'FAILED'
  else:
    return 'SUCCESS'

def get_overview():
  collection_overview = []
  collections = get_all_collections()
  for c in collections:
    collection_overview.append(c)
  # print(collection_overview)
  return collection_overview

def create_coll_index(collection, field):
  db.get_collection(collection).create_index(field)

def find_entries(collection, key, value):
  return db.get_collection(collection).find({key: {'$regex': value}})