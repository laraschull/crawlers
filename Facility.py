class Facility:

    def __init__(self):
        self.name = None
        self.generatedID = None  # change once database is queried

    def setName(self, n, hashMap):
        self.name = n
        try:
            self.generatedID = hashMap[self.name]
        except(KeyError):
            self.generatedID = len(hashMap)+1
            hashMap[self.name] = self.generatedID

    def __str__(self):  # for testing
        ret = ""
        ret = ret + "FACILITY NAME: " + self.name + ",  ID: " + str(self.generatedID) + "\n"
        return ret
