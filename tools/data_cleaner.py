from helper import get_main_dir, get_directories, get_files_in_dir, get_encoding, log

# author: Mario Schuetz
#
# Clean data from special chars etc.
#

log('LB', '')
log('INFO', 'DATA CLEANER Running')
directories = []

special_chars = {
  'ΓöÇ': 'Ä',
  '╬ú': 'ä',
  'Γòô': 'Ö',
  '├╖': 'ö',
  'Γûä': 'Ü',
  'Γü┐': 'ü',
  'ΓûÇ': 'ß',
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


# START
directories = get_files()
for dir in directories:
  clean_spec_chars(dir)

log('INFO', 'DATA CLEANER Done')

