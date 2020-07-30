from helper import get_main_dir, get_directories, get_files_in_dir, get_encoding, log

# author: Mario Schuetz
#
# Change file encoding to utf-8
#

log('LB', '')
log('INFO', 'CONVERTER Running')
directories = []

def get_files():
  directories = get_directories()
  for dir in directories:
    dirname = dir['name']
    dir['files'] = get_files_in_dir(dirname)

  return directories

def change_enc(dir):
  phonebookDir = get_main_dir()
  dirname = dir['name']
  files = dir['files']
  encoding = get_encoding(dirname)
  new_enc = 'utf-8'
  for file in files:

    # only use non utf-8 converted files
    if('utf-8' in file):
      continue
    
    info = f'Converting {dirname} {file} enc= {encoding} to {new_enc}'
    log('INFO', info)

    with open(phonebookDir + dirname + file, 'r', encoding=encoding) as data:
      content = data.read()

    with open(phonebookDir + dirname + file + '_' + new_enc, 'w', encoding=new_enc) as data:
      data = data.write(content)

# START
directories = get_files()
for dir in directories:
  change_enc(dir)

log('INFO', 'CONVERTER Done')
