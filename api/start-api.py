from flask import Flask, jsonify, request
from flask_cors import CORS
from requester import get_all_collections, find_entries

# author: Mario Schuetz
#
# Process api requests
#

app = Flask(__name__)
CORS(app)

@app.route('/all_collections')
def all_collections():
  return get_all_collections()

@app.route('/search')
def search():
  collection = request.args.get('collection')
  if collection is None:
    return 'NO COLLECTION'
  key = request.args.get('key')
  if key is None:
    return 'NO KEY'
  value = request.args.get('value')
  if value is None:
    return 'NO VALUE'

  return jsonify(find_entries(collection, key, value))

if __name__ == '__main__':
  app.run(debug=True)
