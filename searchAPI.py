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
    state = ""
    last = ""
    first = ""

    print(request.args)

    if 'state' in request.args:
        state = request.args['state'].upper()
    else:
        print("Error: No state field provided. Please specify a state.")

    if 'first' in request.args:
        first = request.args['first'].upper()
    else:
        print("Error: No first name field provided. Please specify a first name.")

    if 'last' in request.args:
        last = request.args['last'].upper()
    else:
        print("Error: No last name field provided. Please specify a last name.")

    # instate only records is True by default
    if 'instate' in request.args:
        instate = bool(request.args['instate'])
    else:
        instate = True

    # active only records is True by default
    if 'active' in request.args:
        active = request.args['active'] == "True"
    else:
        active = True

    if state == "GA":
        print("entering Georgia search")
        Crawlers.GeorgiaSearch.baseCrawler(last, first)
        print("exiting search")
    elif state == "NY":
        print("entering New York search")
        Crawlers.NewYorkSearch.baseCrawler(last, first)
        print("exiting search")
    else:
        print("State not found.")

    cursor = db.inmates.find({"name.first": first, "name.last": last})

    print("cursor")
    print(cursor)
    pydictResults = []
    for inmate in cursor:
        print("inmate and type")
        print(inmate)
        print(type(inmate))
        pydictResults += [inmate]
    results = pydictResults

    print("results")
    print(len(results))
    print(results)

    # here, we find the matching record data for each inmate
    for inmate in results:
        print("inmate and type")
        print(inmate)
        print(type(inmate))
        new_records = []
        for record in inmate["records"]:
            new_records += db.records.find({"_id": record})
        inmate["records"] = new_records

    print("initial ret:")
    print(results)

    if instate and active:  # returns only inmates with active and in state records. DEFAULT CASE
        print("returning active, instate records only")
        inStateActiveOnlyResults = []
        for inmate in results:
            for record in inmate["records"]:
                if int(record["status"]) == 1 and record["state"] == state:
                    inStateActiveOnlyResults += [inmate]
                    break
        results = inStateActiveOnlyResults

    elif instate:  # returns only inmates with instate records AT SOME POINT, NOT NECESSARILY ACTIVE
        print("returning instate records only")
        inStateOnlyResults = []
        for inmate in results:
            for record in inmate["records"]:
                if record["state"] == state:
                    inStateOnlyResults += [inmate]
                    break
        results = inStateOnlyResults

    elif active:  # returns only inmates with active records
        print("returning active records only")
        activeOnlyResults = []
        for inmate in results:
            for record in inmate["records"]:
                if int(record["status"]) == 1:
                    activeOnlyResults += [inmate]
                    break
        results = activeOnlyResults

    else:
        print("returning all records")
    # else return all records
    print("returns tests!!!")
    print(results)
    print(type(results))
    print(type(dumps(results)))
    print(type(jsonify(results)))
    return dumps(results)
