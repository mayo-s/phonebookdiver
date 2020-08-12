import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from requester import count_lastnames, get_all_collections

app = Flask(__name__)
CORS(app)



@app.route('/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/count_lastname')
def get_lastname_count():
    return count_lastnames()

@app.route('/all_collections')
def all_collections():
    return get_all_collections()

app.run(debug=True)
