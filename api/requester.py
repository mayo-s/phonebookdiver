import pymongo
from pymongo import MongoClient

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

def count_lastnames():
  try:
    result = get_collection('1998_Q3').count_documents({'lastname': {'$regex': '.*Γü┐.*'}})
  except pymongo.errors.OperationFailure as err:
    print(str(err))
    return 'FAILED'
  else:
    return str(result)
  