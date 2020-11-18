from encoding_converter import encoder
from reader import reader
from uploader import uploader
from db_indexer import create_indexes

def start():
    # encoder()
    reader()
    uploader()
    create_indexes()

start()