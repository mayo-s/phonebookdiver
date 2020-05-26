import os

# Read files
phonebookDir = 'data/phonebooks/'
ignore = ['.DS_Store']
enc = ['cp437', 'iso-8859-1']

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

def get_filedata(dirname, filename):
  encoding = ''
  # choose correct encoding
  year = int(dirname[:4])
  if(year < 2004 and dir != '2003_Q3'):
    encoding=enc[0]
  else:
    encoding=enc[1]
  
  msg = 'YEAR ' + str(year) + ' ENC ' + encoding
  print(msg)

  # with open(phonebookDir + dirname + filename, 'r', encoding=encoding) as data:
  #   for i, line in enumerate(data):
  #     # TODO remove limit
  #     if(i > 42): break
  #     info = str(i) + ' ' + line
  #     print(info)


## WORKFLOW
def do():

  directories = get_directories()
  msg = '# Found ' + str(len(directories)) + ' directories'
  print(msg)

  for dir in directories:
    dir['files'] = get_files_in_dir(dir['name'])
    for file in dir['files']:
      get_filedata(dir['name'], file)

  # test print directories and files
  # for dir in directories:
  #   print(dir['name'])
  #   for file in dir['files']:
  #     print(file)

  return 'SUCCESS'
