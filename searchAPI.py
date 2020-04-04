from flask import Flask, request, jsonify
import Crawlers.GeorgiaSearch as ga_search
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.inmate_database


@app.route('/')
def hello_world():
    return 'hello world'


@app.route('/api/search/')
def search():

    if 'state' in request.args:
        state = request.args['state'].upper()
    else:
        return "Error: No state field provided. Please specify a state."

    if 'first' in request.args:
        first = request.args['first'].upper()
    else:
        return "Error: No first name field provided. Please specify a first name."

    if 'last' in request.args:
        last = request.args['last'].upper()
    else:
        return "Error: No last name field provided. Please specify a last name."

    if state == "GA":
        print("entering Georgia search")
        ga_search.baseCrawler(last, first)
        print("exiting search")
    else:
        return "State Not Found"

    results = db.inmates.find( { "name.first": first, "name.last": last } )

    return dumps(results)