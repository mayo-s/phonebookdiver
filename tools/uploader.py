from helper import get_main_dir, get_directories, get_files_in_dir, get_encoding, log
from mongodb_helper import insert_entries, get_overview
import json

# author: Mario Schuetz
#
# Read json backup file and write data to database
#

collection_overview = get_overview()
directories = []

def get_files():
  directories = get_directories()
  for dir in directories:
    dirname = dir['name']
    dir['files'] = get_files_in_dir(dirname)

  return directories

def get_data_from_file(dir):
  phonebookDir = get_main_dir()
  dirname = dir['name']
  files = dir['files']
  enc = 'utf-8'
  for file in files:
    # only use JSON file
    if('json' not in file):
      continue

    info = f'Caching {dirname}'
    log('INFO', info)
    print(info)

    phonebook_data = []
    with open(phonebookDir + dirname + file, 'r', encoding=enc) as data:
      return json.load(data)


    return None

def send_to_db(collection, phonebook):
  info = f'Inserting into Database {collection}'
  print(info)
  log('INFO', info)
  i = 0
  while i < len(phonebook):
    start = int(i)
    stop = start + 999
    if stop >= len(phonebook):
      stop = len(phonebook) - 1
    entries = phonebook[start:stop]
    resp = insert_entries(entries, collection)
    if resp is 'FAILED':
      print(f'Insert failed {collection} at {start}/{stop}')
      continue
    i += 1000

  return 'SUCCESS'

# WORKFLOW
def uploader():
  log('LB', '')
  log('INFO', 'UPLOAD to DATABASE')
  directories = get_files()
  for dir in directories:
    dirname = dir['name']
    if dirname[:7] not in collection_overview:
      data = get_data_from_file(dir)
      if data is not None:
        collection_name = dirname[:7]
        send_to_db(collection_name, data)
        data.clear()
  print('UPLOADER Done')
  log('INFO', ' UPLOADER Done')
