class Inmate:

    def __init__(self):
        self.generatedID = None
        self.name = None
        self.DOB = None
        # self.id = ""  this category doesn't make sense, as inmate id numbers are usually tied to records. additionally, we generate our own id.
        self.records = []  # list of any previous records
        self.age = None
        self.sex = None
        self.race = None
        self.headshot = None
        self.aliases = []
        self.altIDs = []
        self.records = []

    def addAlias(self, newName):
        if (newName != self.name) and (newName not in self.aliases):
            self.aliases = self.aliases + [newName]
            #self.altIDs = self.altIDs + [hash(newName+self.DOB)]

    def setID(self):
        self.generatedID = hash(self.name+self.DOB)

    def addRecord(self, record):
        self.records = self.records + [record]

    def __str__(self):  # for testing
        ret = ""
        ret = ret + "NAME: " + str(self.name) + "\n"
        ret = ret + "DOB:  " + str(self.DOB) + "\n"
        ret = ret + "RACE: " + str(self.race) + "\n"
        ret = ret + "SEX:  " + str(self.sex) + "\n"
        for x in self.records:
            ret = ret + "Record:  " + str(x.inmateNumber) + " " + str(x.offense) + "\n"
        return ret

