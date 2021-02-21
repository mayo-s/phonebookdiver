from flask import Flask, jsonify, request
from flask_cors import CORS
from requester import get_all_collections, search_colls, fetch_details_by_id, get_federal_states, get_counties
from hm_requester import  hm_query

# author: Mario Schuetz
#
# Process api requests
#

app = Flask(__name__)
CORS(app)

@app.route('/all_collections')
def all_collections():
  return get_all_collections()

@app.route('/hm_search')
def hm_search():
  collection = request.args.get('collection')
  # TODO: should already be checked on frontend!
  if collection is None:
    return 'NO COLLECTION'
  key = request.args.get('key')
  if key is None:
    return 'NO KEY'
  value = request.args.get('value')
  if value is None:
    return 'NO VALUE'

  return jsonify(hm_query(collection, key, value))

@app.route('/federal_states')
def federal_states():
  return jsonify(get_federal_states())

@app.route('/counties')
def counties():
  return jsonify(get_counties())

@app.route('/search')
def search():
  start = request.args.get('start')  
  if start is None:
    return 'INCORRECT RANGE (Start)'
  end = request.args.get('end')
  if end is None:
    return 'INCORRECT RANGE (End)'
  frstkey = request.args.get('frst_key')
  if frstkey is None:
    return 'MISSING KEY'
  frstvalue = request.args.get('frst_value')
  if frstvalue is None:
    return 'MISSING VALUE'
  query_values = { frstkey: frstvalue }

  scndkey = request.args.get('scnd_key')
  scndvalue = request.args.get('scnd_value')
  thrdkey = request.args.get('thrd_key')
  thrdvalue = request.args.get('thrd_value')
  if scndkey is not None and scndvalue is not None:
    query_values[scndkey] = scndvalue
  if thrdkey is not None and thrdvalue is not None:
    query_values[thrdkey] = thrdvalue
  return jsonify(search_colls([start, end], query_values))

@app.route('/fetch_details')
def fetch_details():
  id = request.args.get('id')
  if id is None: return 'INVALID id (fetch details)'

  return jsonify(fetch_details_by_id(id))

if __name__ == '__main__':
  app.run(debug=True)
