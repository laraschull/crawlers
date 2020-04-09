class Facility:

    def __init__(self):
        self.name = None
        self.state = None
        self.generatedID = ""

    def __str__(self):
        return str(self.getDict())

    def getGeneratedID(self):
        self.generatedID = self.state + "_" + self.name.replace(" ", "_")
        return self.generatedID

    def getDict(self):
        return {"_id": self.getGeneratedID(),
                "name": self.name,
                "state": self.state
                }
