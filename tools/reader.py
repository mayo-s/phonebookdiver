from helper import get_main_dir, get_directories, get_files_in_dir, get_encoding, log
from mongodb_helper import upsert_entry, insert_entry, insert_entries
import sys

# author: Mario Schuetz
#
# Read all data and insert into database
#

enc = ['cp437', 'iso-8859-1']
phonebookDir = get_main_dir()
fields = {
  '01_Flags': 'flags',
  '02_Nachname': 'lastname',
  '03_Vorname': 'firstname',
  '04_Namenszusatz': 'name_suffix',  # name abbrevation like 'jr', 'sr'
  '04_Zusaetze': 'name_ext1',  # additional name information
  '04_05_Namenszusatz_Addresszusatz': 'name_ext2',
  '05_Adresszusatz': 'adress_suffix',
  '06_Ortszusatz': 'city_suffix',
  '07_Strasse': 'street',
  '07_Strassenindex': 'street_index',
  '08_Hausnummer': 'street_number',
  '07_08_Strassenindex_Hausnummer': 'street_index_hnr',
  '09_Fax_Verweise': 'fax',
  '09_Verweise': 'reference',
  '10_Postleitzahl': 'zip',
  '10_Zustellamt_PLZOst': 'zip_deloffice',  # zip east delivery office
  '11_Ort': 'city',
  '11_Ort_Gemeinde': 'city_county',
  '12_Vorwahl': 'area_code',
  '13_Rufnummer': 'phonenumber',
  '14_Email': 'email',
  '15_Webadresse': 'webaddress',
  '14_15_Email_Webadresse': 'email_web',
  '16_Koordinaten': 'coordinates',
  '90_Geokoordinaten_hnr': 'geocoords_stnr',
  '91_Geokoordinaten_str': 'geocoords_str',
  '99_Strassenname': 'street_name'
}

def files_to_array(dir):
  dirname = dir['name']
  files = dir['files']
  encoding = get_encoding(dirname)

  info = f'{dirname} ({encoding})'
  print(info)
  log('INFO', info)

  phonebook = []
  for file in files:

    # only use utf-8 converted files
    if('utf-8' not in file):
      continue
    
    info = 'caching ' + dirname + file
    log('INFO', info)

    # ignore utf-8 in filename
    field_name = fields.get(file[:-6], '')
    if field_name is '':
      msg = file + ' does not have a field name'
      log('WARNING', msg)
      continue

    with open(phonebookDir + dirname + file, 'r', encoding=encoding) as data:
      for i, line in enumerate(data):
        if i + 1 >= len(phonebook):
          entry = {}
          entry['_id'] = int(i)
          phonebook.append(entry)

        if line.strip() is '':
          continue

        phonebook[i][field_name] = str(line.strip())

  info = str(len(phonebook)) + ' phonebook entries found'
  log('INFO', info)
  info = str(sys.getsizeof(phonebook)) + ' bytes - current phonebook size'
  log('INFO', info)

  # Write to local file for backup
  with open(phonebookDir + dirname + dirname[:-1] + '_utf-8', 'w', encoding='utf-8') as data:
    for entry in phonebook:
        data.write('%s\n' % entry)
  log('INFO', f'BACKUP file created {dirname[:-1]}')

  return phonebook

def send_to_db(collection, phonebook):
  info = 'Inserting into Database'
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
      print(f'Insert failed {collection}')
      return None
    i += 1000

  return 'SUCCESS'

# WORKFLOW
def start():
  directories = get_directories()
  files = []
  for dir in directories:
    dirname = dir['name']
    dir['files'] = get_files_in_dir(dirname)
    log('INFO', ' -->')
    data = files_to_array(dir)
    collection_name = dirname[:7]
  # send_to_db(collection_name, data)
    del data[:]  # explicitly clear
  print('READER Done.')

  # log('INFO', ' SUCCESS - All files added to database')

start()
