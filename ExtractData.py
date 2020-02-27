from bs4 import BeautifulSoup
from Inmate import Inmate
from InmateRecord import InmateRecord
from Facility import Facility
from datetime import datetime

def inmateRowToList(htmlRow):

    cells = htmlRow.findAll("td")
    parsedData = []

    # splits html row into individual elements in a list
    for cell in cells:
        parsedData += cell.contents

    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    facility = Facility(str(parsedData[3]).strip())  # inmate

    # set inmate name
    allNames = str(parsedData[1]).strip()
    listOfNames = allNames.split(",")
    inmate.lastName = listOfNames[0]
    inmate.firstNames = listOfNames[1]

    # set inmate DOB
    strDOB = str(parsedData[2]).strip()
    listDOB = strDOB.split("/")
    inmate.DOB = datetime(int(listDOB[2]), int(listDOB[0]), int(listDOB[1]))

    # set or find generated ID (deal w/ later)

    # facility.queryID(), implement once database is set up
    fID = facility.getGeneratedID()
    record.setFacilityID(fID)

    print(inmate.firstNames)
    print(inmate.lastName)
    print(inmate.DOB)
    print("\n")






exampleString = '<tr><td><a href="detailsupv.asp?id_inmt_num=269154">269154</a></td><td>AARONS,VINCENT PETER     </td>' \
                '<td>12/7/1964</td><td>WILLARD-CYBULSKI CI                     </td></tr>'

html = BeautifulSoup(exampleString, 'html.parser')  # convert to html before passing to func to mimic website

inmateRowToList(html)