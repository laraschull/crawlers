from flask import Flask, request, jsonify
import Crawlers.GeorgiaSearch
import Crawlers.NewYorkSearch
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

    # instate only records is True by default
    if 'instate' in request.args:
        instate = bool(request.args['instate'])
    else:
        instate = True

    # active only records is True by default
    if 'active' in request.args:
        active = bool(request.args['active'])
    else:
        active = True

    if state == "GA":
        print("entering Georgia search")
        Crawlers.GeorgiaSearch.baseCrawler(last, first)
        print("exiting search")
    if state == "NY":
        print("entering New York search")
        Crawlers.NewYorkSearch.baseCrawler(last, first)
        print("exiting search")
    else:
        return "State Not Found"

    cursor = db.inmates.find({"name.first": first, "name.last": last})

    pydictResults = []
    for inmate in cursor:
        print("inmate and type")
        print(inmate)
        print(type(inmate))
        pydictResults += [inmate]
    results = pydictResults

    # here, we find the matching record data for each inmate
    print("results and type")
    print(results)
    print(type(results))
    for inmate in results:
        print("inmate and type")
        print(inmate)
        print(type(inmate))
        new_records = []
        for record in inmate["records"]:
            new_records += db.records.find({"_id": record})
        inmate["records"] = new_records

    if instate and active:  # returns only inmates with active and in state records. DEFAULT CASE
        inStateActiveOnlyResults = []
        for inmate in results:
            for record in inmate["records"]:
                if int(record["status"]) == 1 and record["state"] == state:
                    inStateActiveOnlyResults += [inmate]
                    break
        results = inStateActiveOnlyResults

    elif instate:  # returns only inmates with instate records
        inStateOnlyResults = []
        for inmate in results:
            for record in inmate["records"]:
                if record["state"] == state:
                    inStateOnlyResults += [inmate]
                    break
        results = inStateOnlyResults

    elif active:  # returns only inmates with active records
        activeOnlyResults = []
        for inmate in results:
            for record in inmate["records"]:
                if int(record["status"]) == 1:
                    activeOnlyResults += [inmate]
                    break
        results = activeOnlyResults

    # else return all records

    return jsonify(results)
