import os
import sys
import logging
import datetime
from datetime import datetime

# author: Mario Schuetz
#
# Provide functionality across project
#

phonebookDir = 'data/'
ignore = ['.DS_Store', 'archive', 'yellow_2017_Q3', '90_Geokoordinaten_hnr', '91_geokoordinaten_str', '99_Strassenname', '90_Geokoordinaten_hnr_utf-8', '91_geokoordinaten_str_utf-8', '99_Strassenname_utf-8']
logging.basicConfig(filename='_phonebookdiver.log', level=logging.DEBUG)
encoding = ['cp437', 'iso-8859-1']

def log(type, msg):
  date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
  msg = ' ' + date_time + ' ' + msg
  if type is 'WARNING':
    logging.warning(msg)
  if type is 'INFO':
    logging.info(msg)
  if type is 'LB':
    logging.info('')

def get_main_dir():
  return phonebookDir

# Get all directories by name
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
  info = ' # Found ' + str(len(directories)) + ' directories'
  log('INFO', info)
  return directories

# Get all files by name in directory
def get_files_in_dir(dir):
  files = []
  for filename in os.listdir(phonebookDir + dir):
    if filename not in ignore:
      files.append(filename)
  return files

# Get file encoding by year (split string)
def get_encoding(dirname):
  year = int(dirname[:4])
  if(year < 2004 and dir != '2003_Q3'):
    return encoding[0]
  else:
    return encoding[1]
