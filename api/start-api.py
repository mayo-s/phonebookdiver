from flask import Flask, jsonify, request
from flask_cors import CORS
from requester import get_all_collections, find_entries, search_colls

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

  return jsonify(find_entries(collection, key, value))

@app.route('/search')
def search():
  start = request.args.get('start')
  end = request.args.get('end')
  key = request.args.get('key')
  value = request.args.get('value')

  return jsonify(search_colls(start, end, key, value))



if __name__ == '__main__':
  app.run(debug=True)
