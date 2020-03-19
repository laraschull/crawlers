class InmateRecord:

    def __init__(self):

        self.generatedID = None
        self.inmateNumber = None  # in NY this is called DIN
        self.admissionDate = None  # in NY this is called Date Received (Current)
        self.sentenceDate = None  # not available in NY db
        self.maxReleaseDate = None  # in NY db, this is called Maximum Expiration Date
        self.estReleaseDate = None  # in NY db, this is called Conditional Release Date
        self.facilityID = None
        self.bondAmt = None  # not available in NY db
        self.status = ""
        self.offense = ""
        self.offenseClass = ""

        # additional NY fields:
        self.admissionType = None
        self.county = None

    def __str__(self):  # for testing
        ret = ""
        ret = ret + "generatedID: " + str(self.generatedID) + "\n"
        ret = ret + "inmateNumber: " + str(self.inmateNumber) + "\n"
        ret = ret + "admissionDate: " + str(self.admissionDate) + "\n"
        ret = ret + "sentenceDate: " + str(self.sentenceDate) + "\n"
        ret = ret + "maxReleaseDate: " + str(self.maxReleaseDate) + "\n"
        ret = ret + "estReleaseDate: " + str(self.estReleaseDate) + "\n"
        ret = ret + "facilityID: " + str(self.facilityID) + "\n"
        ret = ret + "bondAmt: " + str(self.bondAmt) + "\n"
        ret = ret + "status: " + str(self.status) + "\n"
        ret = ret + "offense: " + str(self.offense) + "\n"
        ret = ret + "offenseClass: " + str(self.offenseClass) + "\n"
        ret = ret + "admissionType: " + str(self.admissionType) + "\n"
        ret = ret + "county: " + str(self.county) + "\n"
        return ret

