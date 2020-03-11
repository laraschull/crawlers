from enum import Enum
class RecordStatus(Enum):
    UNDEFINED = -1
    INACTIVE = 0
    ACTIVE = 1

class InmateRecord:
    status = RecordStatus
    def __init__(self):
        self.generatedID = None
        self.inmateNumber = None
        self.admissionDate = None
        self.sentenceDate = None
        self.maxReleaseDate = None
        self.estReleaseDate = None
        self.facilityID = None
        self.bondAmt = None
        self.status = RecordStatus.UNDEFINED
        self.offense = ""

    def __setattr__(self, name, value):
        if name == 'status' and not isinstance(value, RecordStatus):
            raise TypeError('Status must be of type RecordStatus')
        super().__setattr__(name, value)