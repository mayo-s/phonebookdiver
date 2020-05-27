from pymongo import MongoClient

MONGO_URI = 'mongodb://localhost:27017'
client = MongoClient(MONGO_URI)
db = client.phonebookdiver

def create_collection(name):
  collection = db[name]

def insert_entry(entry, collection):
  collection.insert_one(entry)

def insert_entries(entries, collection):
  collection.insert_many(entries)
