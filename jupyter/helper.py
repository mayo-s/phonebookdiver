import time
import logging
import datetime
from datetime import datetime
import numpy as np
import pandas as pd

logging.basicConfig(filename='./archive/_phonebookdiver-notebook.log', level=logging.DEBUG)

def get_phonebooks(db):
    ignore = ['geodata', 'counties', 'states', 'zips_cities_counties_states']
    collections = []
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
    return convert_time(time_since)

def convert_time(time_value):
    if time_value >= 5400: return str(time_value/3600) + ' hours'
    elif time_value >= 180: return str(time_value/60) + ' minutes'
    return str(time_value) + ' seconds'

# Add collection and a list of values to specify filename
def export_results(results, collection, values, with_index):
    path = r'./' + values[0] + '/'+ collection
    for v in values:
        path += '_' + v
    path += '.csv'
    results.to_csv(path, index=with_index)

def create_collection(db, collection_name, dataframe, reset_index):
    start = time.time()
    if collection_name in db.list_collection_names(): 
        return f'Collection {collection_name} already exists.'
    dataframe.reset_index(inplace=reset_index)
    data_dict = dataframe.to_dict("records")
    db[collection_name].insert_many(data_dict)
    t = elapsed_time(start, time.time())
    return f'Collection {collection_name} successfully inserted. {t}'

# create new INDEX in all collections
def create_index_on_fields(db, collections, field_names):
    msg = 'Create indices'
    print(msg)
    log('INFO', msg)
    _start = time.time()
    for field_name in field_names:
        for c in collections:
            start = time.time()
            db.get_collection(c).create_index(field_name)
            msg = f'Index created on {c} {field_name} - processing time {elapsed_time(start, time.time())}'
            print(msg)
            log('INFO', msg)
    msg  = f'{len(field_names)} indecies created in {elapsed_time(_start, time.time())}'
    log('INFO', msg)
    return msg
    # 5152.3292899131775 seconds [area_code] (85 minutes)
    # 4967.730529785156 seconds , #2 '4937.383540868759 seconds' [zip]
    # 5070.640741109848 seconds [city]

def value_counts_from_df(collection, df, values):
    val_counts_df = pd.DataFrame(df.value_counts(values))
    value_counts_df = val_counts_df.reset_index()
    value_counts_df.columns = [f'unique_{values[0]}', 'count']
    return value_counts_df