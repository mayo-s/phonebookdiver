import os
import mongodb_helper
from mongodb_helper import upsert_entry

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
    '10_Postleitzahlen': 'zip',
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


def get_fieldname(filename):
    field_name = ''
    field_id = filename[:2]

    return field_name


def save_entries_to_db(dirname, filename):
    encoding = ''
    # choose correct encoding
    year = int(dirname[:4])
    if(year < 2004 and dir != '2003_Q3'):
        encoding = enc[0]
    else:
        encoding = enc[1]

    collection_name = dirname[:7]
    field_name = fields.get(filename, '')
    if field_name is None:
        err = 'ERROR: Filename not found - ' + filename
        print(err)
        return err

    print('Reading file...')
    entries = []
    with open(phonebookDir + dirname + filename, 'r', encoding=encoding) as data:
        for i, line in enumerate(data):
            if line.strip() == '':
                continue

            entry = {field_name: line.strip()}
            id = {'_id': i}
            upsert_entry(id, entry, collection_name)

    return 'SUCCESS - file added to DB'

# WORKFLOW
directories = get_directories()
print('# Found ', str(len(directories)), ' directories')

for dir in directories:
  dir['files'] = get_files_in_dir(dir['name'])
  print('-->')
  for file in dir['files']:
    print('# ', dir['name'], file)
    save_entries_to_db(dir['name'], file)
print('SUCCESS - All files added to database')
