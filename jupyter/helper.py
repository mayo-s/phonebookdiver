import time
import logging
import datetime
from datetime import datetime
import numpy as np
import pandas as pd

logging.basicConfig(filename='./archive/_phonebookdiver-notebook.log', level=logging.DEBUG)
db = None
collections = []

def get_phonebooks(database):
    db = database
    collections = []
    ignore = ['geodata', 'counties', 'states', 'zips_cities_counties_states']
    for key in dict.fromkeys(db.list_collection_names(), 'name'):
        collections.append(key)
    collections.sort()
    # remove collections that are not a phone book
    for i in ignore:
        if i in collections:
            collections.remove(i)
    return collections

def log(type, msg):
    date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    msg = ' ' + date_time + ' ' + msg
    if type == 'WARNING':
        logging.warning(msg)
    if type == 'INFO':
        logging.info(msg)
    if type == 'LB':
        logging.info('')

def elapsed_time(start, end):
    time_since = end - start
    return str(time_since) + ' seconds'

# Add collection and a list of values to specify filename
def export_results(results, collection, values, with_index):
    path = r'./' + values[0] + '/'+ collection
    for v in values:
        path += '_' + v
    path += '.csv'
    results.to_csv(path, index=with_index)
    
def get_record_by_id(collection, id):
    return pd.DataFrame(db[collection].find({'_id': id}))

def trace_phonenr(area_code, phone_nr):
    records = []
    for  c in collections:
        record = db[c].find_one({'area_code': area_code, 'phonenumber': phone_nr})
        if record is not None:
            record['collection'] = c
            records.append(record)

    return pd.DataFrame(records)

def create_collection(collection_name, dataframe, reset_index):
    start = time.time()
    if collection_name in db.list_collection_names(): 
        return f'Collection {collection_name} already exists.'
    dataframe.reset_index(inplace=reset_index)
    data_dict = dataframe.to_dict("records")
    db[collection_name].insert_many(data_dict)
    t = elapsed_time(start, time.time())
    return f'Collection {collection_name} successfully inserted. {t}'

# create new INDEX in all collections
def create_index_on_fields(field_names):
    start = time.time()
    for field_name in field_names:
        for c in collections:
            db.get_collection(c).create_index(field_name)
        print(f'{field_name} {elapsed_time(start, time.time())}')
    return elapsed_time(start, time.time())
    # 5152.3292899131775 seconds [area_code] (85 minutes)
    # 4967.730529785156 seconds , #2 '4937.383540868759 seconds' [zip]
    # 5070.640741109848 seconds [city]
    
def create_index_on_field(field_name):
    start = time.time()
    for c in collections:
        db.get_collection(c).create_index(field_name)
    return elapsed_time(start, time.time())
