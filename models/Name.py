class Name:

    def __init__(self, first, middle, last):
        self.first = first.upper()
        self.middle = middle.upper()  # put everything but very first and very last here to keep names consistent
        self.last = last.upper()

    def __eq__(self, obj):
        return self.first == obj.first and self.middle == obj.middle and self.last == obj.last

    def __hash__(self):
        return hash(self.first + " " + self.middle + " " + self.last)

    def __str__(self):
        return self.first + (" " if len(self.middle) > 0 else "") + self.middle + " " + self.last

    def getDict(self):
        return {"first": self.first, "middle": self.middle, "last": self.last}

    def setByDict(self, param):
        self.first = param["first"]
        self.middle = param["middle"]
        self.last = param["last"]