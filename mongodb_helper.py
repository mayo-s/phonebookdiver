import pymongo
from pymongo import MongoClient
from log_helper import log

MONGO_URI = 'mongodb://localhost:27017'

try:
  client = MongoClient(MONGO_URI)
  db = client.phonebookdiver 
except pymongo.errors as err:
  log('LB', '')
  log('WARNING', err)
else:
  log('LB', '')
  info = 'CONNECTED to ' + MONGO_URI + db.name
  log('INFO', info)

def get_database():
  return db

def get_collection(name):
    return db[name]

def insert_entry(entry, collection):
  c = get_collection(collection)
  c.insert_one(entry)

def insert_entries(entries, collection):
  c = get_collection(collection)
  c.insert_many(entries)

def upsert_entry(id, entry, collection):
  c = get_collection(collection)
  c.update(id, entry, upsert=True)
