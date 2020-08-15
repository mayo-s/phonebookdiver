from helper import get_main_dir, get_directories, get_files_in_dir, get_encoding, log

# author: Mario Schuetz
#
# Clean data from special chars etc.
#

log('LB', '')
log('INFO', 'DATA CLEANER Running')
directories = []

# Umlaut  File    Database
# Ä =     ─       ΓöÇ       
# ä =     Σ       ╬ú
# Ö =     ╓       Γòô
# ö =     ÷       ├╖
# Ü =     ▄       Γûä
# ü =     ⁿ       Γü┐
# ß =     ▀       ΓûÇ
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

    with open(phonebookDir + dirname + file, 'r', encoding=enc) as data:
      content = data.read()

    for line in content:
      line = check_substring(line)

    with open(phonebookDir + dirname + file, 'w', encoding=enc) as data:
      data = data.write(content)

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

