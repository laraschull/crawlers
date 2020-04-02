from enum import Enum
from models.Date import Date
from utils.identifier import *

class RecordStatus(Enum):
    UNDEFINED = -1
    INACTIVE = 0
    ACTIVE = 1

class InmateRecord:
    status = RecordStatus
    def __init__(self):
        self.generatedID = ""
        self.inmateNumber = None
        self.recordNumber = None
        self.admissionDate = None
        self.sentenceDate = None
        self.maxReleaseDate = None
        self.estReleaseDate = None
        self.paroleEligibilityDate = None
        self.nextParoleHearingDate = None
        self.facility = None
        self.state = None
        self.bondAmt = None
        self.status = RecordStatus.UNDEFINED
        self.offense = ""

    def __str__(self):
        return str(self.getDict())

    def __setattr__(self, name, value):
        if name == 'status' and not isinstance(value, RecordStatus):
            raise TypeError('Status must be of type RecordStatus')
        super().__setattr__(name, value)

    def getGeneratedID(self):
        if (len(self.generatedID) == 0):
            self.generatedID = generate_record_id(self.state, self.recordNumber)
        return self.generatedID

    def getDict(self):
        if(not isinstance(self.admissionDate, Date) and self.admissionDate is not None):
            self.admissionDate = Date(self.admissionDate.year, self.admissionDate.month, self.admissionDate.day)
        if (not isinstance(self.sentenceDate, Date) and self.sentenceDate is not None):
            self.sentenceDate = Date(self.sentenceDate.year, self.sentenceDate.month, self.sentenceDate.day)
        if (not isinstance(self.maxReleaseDate, Date) and self.maxReleaseDate is not None):
            self.maxReleaseDate = Date(self.maxReleaseDate.year, self.maxReleaseDate.month, self.maxReleaseDate.day)
        if (not isinstance(self.admissionDate, Date) and self.estReleaseDate is not None):
            self.estReleaseDate = Date(self.estReleaseDate.year, self.estReleaseDate.month, self.estReleaseDate.day)

        return{
            "_id": generate_record_id(self.state, self.recordNumber),  # db key!
            "inmateNumber": self.inmateNumber,
            "inmateID": self.inmateID,  # db key!
            "recordNumber": self.recordNumber,
            "admissionDate": self.admissionDate.getDict() if self.admissionDate is not None else None,
            "sentenceDate": self.sentenceDate.getDict() if self.sentenceDate is not None else None,
            "maxReleaseDate": self.maxReleaseDate.getDict() if self.maxReleaseDate is not None else None,
            "estReleaseDate": self.estReleaseDate.getDict() if self.estReleaseDate is not None else None,
            "paroleEligibilityDate": self.paroleEligibilityDate,
            "nextParoleHearingDate": self.nextParoleHearingDate,
            "facilityID": self.facilityID,  # db key!
            "state": self.state,
            "bondAmt": self.bondAmt,
            "status": self.status.value,
            "offense": self.offense,
        }

    def addFacility(self, facility):
        self.facility = facility
