from helper import get_main_dir, get_directories, get_files_in_dir, get_encoding, log
from mongodb_helper import get_all_collections, find_entries, update_doc
import json

# author: Mario Schuetz
#
# Clean data from special chars etc.
#

special_chars = {
  # records until 2003
  'ΓöÇ': 'Ä',
  '╬ú': 'ä',
  'Γòô': 'Ö',
  '├╖': 'ö',
  'Γûä': 'Ü',
  'Γü┐': 'ü',
  'ΓûÇ': 'ß',
  # records after 2003
  'Ã': 'Ä',
  'Ã¤': 'ä',
  'Ã': 'Ö',
  'Ã¶': 'ö',
  'Ã': 'Ü',
  'Ã¼': 'ü',
  'Ã': 'ß',
}

def get_files():
  directories = get_directories()
  for dir in directories:
    dirname = dir['name']
    dir['files'] = get_files_in_dir(dirname)

  return directories

def clean_spec_chars(dir):
  phonebookDir = get_main_dir()
  dirname = dir['name']
  files = dir['files']
  enc = 'utf-8'
  for file in files:

    # # only use utf-8 converted files
    # if('utf-8' not in file):
    #   continue
    
    # clean only backup file
    info = f'Cleaning {dirname} {file}'
    log('INFO', info)

    cleaned_data = []
    with open(phonebookDir + dirname + file, 'r', encoding=enc) as data:
      line = data.readline()
      while line:
        line = check_substring(line)
        cleaned_data.append(line)
        line = data.readline()

    with open(phonebookDir + dirname + file + '_new', 'w', encoding=enc) as data:
      for entry in cleaned_data:
        data.write('%s\n' % entry)

def check_substring(line):
  for sc in special_chars:
    while sc in line: 
    	line = line.replace(sc, special_chars.get(sc))

  return line

def remove_char(elem, char):
  while char in elem:
    elem = elem.replace(char, '')
  return elem

# remove spaces from street numbers and capitalize letters
# def clean_hnr():
#   key_name = 'street_number'
#   # collections = get_all_collections()

#   collections = ['1992_Q2']

#   for coll in collections: 
#     info = f'{coll} Cleaning street numbers'
#     log('INFO', info)
#     print(info)    
#     for e in find_entries(coll, key_name, '.* .*'):
#       e[key_name] = remove_char(e.get(key_name), ' ').upper().strip()
#       print(f"{coll} {e['_id']} {key_name} {e.get(key_name)}")

#       # update_doc(coll, e['_id'], key_name, e.get(key_name))
#   print('DONE')
#   return 'DONE'

def clean_city():
  key_name = 'city'
  collections = get_all_collections()

  for coll in collections: 
    info = f'{coll} Cleaning city names'
    log('INFO', info)
    print(info)    
  # db.getCollection('1997_Q1').find({'city': {$regex: '.*\\*.*'}})
    for e in find_entries(coll, key_name, '.*\\*.*'):
      e[key_name] = remove_char(e.get(key_name), '*').strip()
      
      update_doc(coll, e['_id'], key_name, e.get(key_name))
  print('DONE')
  return 'DONE'


# START
def start():
  log('LB', '')
  log('INFO', 'DATA CLEANER Running')
  directories = get_files()
  for dir in directories:
    clean_spec_chars(dir)

  log('INFO', 'DATA CLEANER Done')
