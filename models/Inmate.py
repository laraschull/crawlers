from utils.identifier import *
from models.Name import Name
from models.Date import Date

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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            print("classes unequal")
            return False
        if not self.name == other.name:
            print("names unequal")
            return False
        if not self.DOB == other.DOB:
            print("DOBs unequal")
            return False
        # TODO add more tests
        return True

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

    def setByDict(self, param):
        self.name = Name().setByDict(param["name"])
        self.DOB = Date().setByDict(param["DOB"])
        # TODO set other fields
