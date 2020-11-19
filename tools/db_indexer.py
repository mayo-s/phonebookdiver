from mongodb_helper import get_all_collections, create_coll_index
from helper import log


def create_indexes():
  log('INFO', 'INDEXING')
  collections = get_all_collections()
  for c in collections:
    log('INFO', f'Creating indexes for {c}')
    print(f'Creating index for {c}')
    create_coll_index(c, 'lastname')
    create_coll_index(c, 'firstname')

  print('Indexing DONE')
  
# create_indexes()