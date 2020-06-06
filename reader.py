import os
from mongodb_helper import upsert_entry
from log_helper import log

# Read files
phonebookDir = 'data/'
ignore = ['.DS_Store', 'archive', 'yellow_2017_Q3']
enc = ['cp437', 'iso-8859-1']
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
    '08_Hausnummer': 'street_number',
    '07_08_Strassenindex_Hausnummer': 'street_index',
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
    '91_geokoordinaten_str': 'geocoords_str',
    '99_Strassenname': 'street_name'
}

def get_directories():
    directories = []
    for dirname in os.listdir(phonebookDir):
        if dirname not in ignore:
            dirname += '/'
            dir = {
                'name': dirname,
                'files': [],
            }
            directories.append(dir)
    return directories


def get_files_in_dir(dir):
    files = []
    for filename in os.listdir(phonebookDir + dir):
        if filename not in ignore:
            files.append(filename)
    return files


def get_encoding(dirname):
# choose correct encoding
    year = int(dirname[:4])
    if(year < 2004 and dir != '2003_Q3'):
        return enc[0]
    else:
        return enc[1]
    

# def save_entries_to_db(dirname, filename):

#     info = ' Saving --> ' + dir['name'] + file
#     log('INFO', info)
#     encoding = get_encoding(dirname)
#     collection_name = dirname[:7]
#     field_name = fields.get(filename, '')
#     if field_name is None:
#         err = 'ERROR: Filename not found - ' + filename
#         log('WARNING', err)
#         return err

#     log('INFO', 'Reading file...')
#     entries = []
#     with open(phonebookDir + dirname + filename, 'r', encoding=encoding) as data:
#         for i, line in enumerate(data):
#             if line.strip() == '':
#                 continue

#             entry = {field_name: line.strip()}
#             id = {'_id': i}
#             upsert_entry(id, entry, collection_name)

#     info = ' SUCCESS - file added to DB'
#     log('INFO', info)
#     return info


def files_to_array(dir):
    dirname = dir['name']
    files = dir['files']
    encoding = get_encoding(dirname)
    phonebook = []
    for file in files:
        info = 'caching ' + dirname + file
        log('INFO', info)
        field_name = fields.get(file, '')
        if field_name is '':
            msg = file + ' does not have a field name'
            log('WARNING', msg)
            continue
        with open(phonebookDir + dirname + file, 'r', encoding=encoding) as data:
            for i, line in enumerate(data):
                if i >= len(phonebook):
                    entry = {'_id': i}
                    phonebook.append(entry)
                
                if line.strip() == '':
                    continue

                phonebook[i][field_name] = line.strip()
    info = str(len(phonebook)) + ' phonebook entries found'
    log('INFO', info)
    for p in phonebook[:100]:
        print(p)

    return phonebook

def send_to_db(collection, phonebook):
    print('Inserting into Database')
    for entry in enumerate(phonebook):
        id = entry['_id']
        upsert_entry(id, entry, collection)

    return 'SUCCESS'


# WORKFLOW

directories = get_directories()
info = ' # Found ' + str(len(directories)) + ' directories'
log('INFO', info)
files = []
for dir in directories:
    dirname = dir['name']
    dir['files'] = get_files_in_dir(dirname)
    log('INFO', ' -->')
    # for file in dir['files']:
    #     save_entries_to_db(dir['name'], file)
    data = files_to_array(dir)
    send_to_db(dirname[:7], data)

log('INFO', ' SUCCESS - All files added to database')
