from flask import Flask, request, jsonify
import Crawlers.GeorgiaSearch
import Crawlers.NewYorkSearch
import Crawlers.MaineSearch
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
        instate = request.args['instate'][0:1].upper() == "T"
    else:
        instate = True

    # active only records is True by default
    if 'active' in request.args:
        active = request.args['active'][0:1].upper() == "T"
    else:
        active = True

    if state == "GA":
        print("Entering Georgia search...")
        Crawlers.GeorgiaSearch.baseCrawler(last, first)
        print("Exiting Georgia search!")
    elif state == "NY":
        print("Entering New York search...")
        Crawlers.NewYorkSearch.baseCrawler(last, first)
        print("Exiting New York search!")
    elif state == "ME":
        print("Entering Maine search...")
        Crawlers.MaineSearch.baseCrawler(last, first)
        print("Exiting Maine search!")
    else:
        print("State not found.")

    cursor = db.inmates.find({"name.first": first, "name.last": last})

    pydictResults = []
    for inmate in cursor:
        pydictResults += [inmate]
    results = pydictResults

    # here, we find the matching record data for each inmate
    for inmate in results:
        new_records = []
        for record in inmate["records"]:
            new_records += db.records.find({"_id": record})
        inmate["records"] = new_records

    if instate and active:  # returns only inmates with active and in state records. DEFAULT CASE
        print("Returning instate, active inmates that meet search query.")
        inStateActiveOnlyResults = []
        for inmate in results:
            for record in inmate["records"]:
                if int(record["status"]) == 1 and record["state"] == state:
                    inStateActiveOnlyResults += [inmate]
                    break
        results = inStateActiveOnlyResults

    elif instate:  # returns only inmates with instate records AT SOME POINT, NOT NECESSARILY ACTIVE
        print("Returning all instate inmates that meet search query.")
        inStateOnlyResults = []
        for inmate in results:
            for record in inmate["records"]:
                if record["state"] == state:
                    inStateOnlyResults += [inmate]
                    break
        results = inStateOnlyResults

    elif active:  # returns only inmates with active records
        print("Returning all active inmates that meet search query.")
        activeOnlyResults = []
        for inmate in results:
            for record in inmate["records"]:
                if int(record["status"]) == 1:
                    activeOnlyResults += [inmate]
                    break
        results = activeOnlyResults

    else:
        print("Returning all inmates that meet search query.")

    return dumps(results)
