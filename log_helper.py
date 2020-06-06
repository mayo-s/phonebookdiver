import logging
import datetime
from datetime import datetime

logging.basicConfig(filename='_phonebookdiver.log', level=logging.DEBUG)

def log(type, msg):
    date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    msg = ' ' + date_time + ' ' + msg
    if type is 'WARNING':
        logging.warning(msg)
    if type is 'INFO':
        logging.info(msg)
    if type is 'LB':
        logging.info('')