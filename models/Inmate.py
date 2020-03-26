from utils.identifier import *

class Inmate:

    def __init__(self):
        self.generatedID = ""  # ALWAYS USE THE getGeneratedID method!
        self.name = None
        self.DOB = None  # can be a Date object
        self.records = []  # list of any previous/current records
        self.sex = None
        self.race = None
        self.headshot = None
        self.eyeColor = None
        self.height = None 
        self.weight = None
        self.hairColor = None

    def getGeneratedID(self):
        if (len(self.generatedID) == 0):
            self.generatedID = generate_inmate_id(self.name, self.DOB)
        return self.generatedID

    def addRecord(self, record):
        record.inmateID = self.getGeneratedID()
        if record.getGeneratedID() not in [x.getGeneratedID() for x in self.records]:
            self.records += [record]

    def getDict(self):

        return {"_id": self.getGeneratedID(),
                "name": self.name.getDict(),
                "DOB": self.DOB.getDict(),
                "records": [x.getGeneratedID() for x in self.records],  # if we only want the record ids to be saved!
                "sex": self.sex,
                "race": self.race,
                "headshot": self.headshot,
                "eyecolor": self.eyeColor,
                "height": self.height,
                "weight": self.weight,
                "hairColor": self.hairColor
        }