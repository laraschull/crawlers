from utils.identifier import *
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.inmate_database


def updateInmate(inmate):
    # TODO, make updater intelligently reconcile the data, rather than simply overwrite it
    db.inmates.delete_one({"_id": inmate.getGeneratedID()})
    db.inmates.insert_one(inmate.getDict())


def updateRecord(record):
    # TODO, make updater intelligently reconcile the data, rather than simply overwrite it
    db.records.delete_one({"_id": record.getGeneratedID()})
    db.records.insert_one(record.getDict())


def writeToDB(inmate):
    if(db.inmates.count_documents({"_id": generate_inmate_id(inmate)}) == 0):  # insert new inmate
        print("new inmate")
        db.inmates.insert_one(inmate.getDict())
    else:  # update existing inmate
        print("repeat inmate")
        updateInmate(inmate)  # from utils.updater

    for rec in inmate.records:
        if (db.records.count_documents({"_id": rec.getGeneratedID()}) == 0):  # insert new record
            print("new record")
            db.records.insert_one(rec.getDict())
        else:  # update existing record
            print("repeat record")
            updateRecord(rec)  # from utils.updater
        if(rec.facility is not None):
            if (db.facilities.count_documents({"_id": rec.facility.getGeneratedID()}) == 0):  # insert new record
                print("new facility")
                db.facilities.insert_one(rec.facility.getDict())
            else:  # update existing record
                print("repeat facility")