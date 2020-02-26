class Facility:

    def __init__(self, name):

        self.name = name
        self.generatedID = 1 #change once database is queried


    def getName(self):

        return self.name

    def setName(self, name):

        self.name = name

    def getGeneratedID(self):

        return self.generatedID