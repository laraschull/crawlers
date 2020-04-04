class Facility:

    def __init__(self):
        self.name = None
        self.state = None
        # self.generatedID = self.state + "_" + self.name

    def getDict(self):
        return {"_id": self.generatedID,
                "name": self.name,
                "state": self.state
                }

    def getGeneratedID(self):
        return self.generatedID