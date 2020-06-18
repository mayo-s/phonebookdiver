import os
from mongodb_helper import upsert_entry, insert_entry, insert_entries
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
                if i + 1 >= len(phonebook):
                    entry = {}
                    entry['_id'] = int(i)
                    phonebook.append(entry)
                
                if line.strip() == '':
                    continue

                # phonebook[i][field_name] = line.strip()
    info = str(len(phonebook)) + ' phonebook entries found'
    log('INFO', info)

    return phonebook

def send_to_db(collection, phonebook):
    info = 'Inserting into Database'
    print(info)
    log('INFO', info)
    # for entry in phonebook:
    #     insert_entry(entry, collection)
    i = 0
    while i < len(phonebook):
        start = int(i)
        stop = start + 999
        if stop >= len(phonebook):
            stop = len(phonebook) -1
        entries = phonebook[start:stop]
        insert_entries(entries, collection)
        i += 1000

    return 'SUCCESS'


# WORKFLOW

directories = get_directories()
info = ' # Found ' + str(len(directories)) + ' directories'
log('INFO', info)
files = []
total_entries = 0
for dir in directories:
    dirname = dir['name']
    dir['files'] = get_files_in_dir(dirname)
    log('INFO', ' -->')
    # for file in dir['files']:
    #     save_entries_to_db(dir['name'], file)
    data = files_to_array(dir)
    total_entries += len(data)
    send_to_db(dirname[:7], data)
    info = ' Number of total entries added to database' + total_entries
    log('INFO', info)
    data = [] # explicitly clear

log('INFO', ' SUCCESS - All files added to database')
