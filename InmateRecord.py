import datetime

class InmateRecord:

    def __init__(self):

        self.generatedID = None
        self.inmateNumber = None
        self.admissionDate = None
        self.sentenceDate = None
        self.maxReleaseDate = None
        self.estReleaseDate = None
        self.facilityID = None
        self.bondAmt = None
        self.status = ""
        self.offense = ""


    def getFacilityID(self):

        return self.facilityID

    def setFacilityID(self, i):

        self.facilityID = i