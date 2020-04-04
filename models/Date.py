from datetime import datetime
from datetime import timedelta


class Date:
    year = None
    month = None
    day = None
    estimated = False
    def __init__(self, year, month=None, day=None, estimated=False):

        if year == "N/A" or year == "LIFE" or year == "NOT":
            return
        elif isinstance(year, str) and "/" in year:
            try:
                [m, d, y] = year.split("/")
                self.day = int(d)
                self.month = int(m)
                self.year = int(y)
            except(ValueError):
                return
        else:
            if day is not None:
                self.day = int(day)
            if month is not None:
                self.month = int(month)
            self.year = int(year)
        self.estimated = estimated

    def ageToDate(age):
        return Date()

    def __eq__(self, obj):
        return self.day == obj.day and self.month == obj.month and self.year == obj.year

    def __str__(self):
        return str(self.month)+"/"+str(self.day)+"/"+str(self.year)+"(estimate)"if self.estimated else""

    def getDict(self):
        return {"day": self.day, "month": self.month, "year": self.year, "estimated": self.estimated}

    def setByDict(self, param):
        self.day = int(param["day"])
        self.month = int(param["month"])
        self.year = int(param["year"])
        self.estimated = bool(param["estimated"])

    def addTime(self, y, m, d):
        try:
            datetimeObj = datetime(self.year, self.month, self.day) + timedelta(days=d, weeks=4*m + 52*y)
        except(TypeError):
            return
        self.year = datetimeObj.year
        self.month = datetimeObj.month
        self.day = datetimeObj.day
