import pymongo
from pymongo import MongoClient

MONGO_URI = 'mongodb://localhost:27017'
try:
  client = MongoClient(MONGO_URI)
  db = client.phonebookdiver 
except pymongo.errors as err:
  print(err)
else:
  print('CONNECTED to ', db.name)

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
