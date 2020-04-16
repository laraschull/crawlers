class Facility:

    def __init__(self):
        self.name = None
        self.state = None
        self.generatedID = ""

    def getGeneratedID(self):
        self.generatedID = self.state + "_" + self.name.replace(" ", "_")
        return self.generatedID

    def getDict(self):
        return {"_id": self.getGeneratedID(),
                "name": self.name,
                "state": self.state
                }

    def getGeneratedID(self):
        if self.generatedID is not None:
            self.generatedID = self.name + self.state
        return self.generatedID
