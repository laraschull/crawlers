from selenium import webdriver
from string import ascii_lowercase
from bs4 import BeautifulSoup
from models.Name import Name
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from datetime import datetime
import time
import re


def checkIfWeHaveRow(hash_from_birthdays_to_used_names, htmlRow, browser):

    # currently still html
    cells = htmlRow.findAll("td")
    parsedData = []
    # splits html row into individual elements in a list
    for cell in cells:
        parsedData += cell.contents
    rawName = parsedData[3]
    last = rawName.split(',')[0]
    firsts = rawName.split(',')[1].strip()
    fname = firsts.split(" ")[0].strip()
    try:
        mname = firsts.split(" ")[1].strip()
    except(IndexError):
        mname = ""
    lname = last.strip()
    name = Name(fname, mname, lname)

    dob = parsedData[5]
    dob = dob.split("/")
    dob = datetime(int(dob[2]), int(dob[0]), int(dob[1]))

    print(name)
    print(dob)
    try:
        print(name in hash_from_birthdays_to_used_names[dob])
        return (name in hash_from_birthdays_to_used_names[dob])
    except(KeyError):
        return False


def crawl():
    browser = webdriver.Chrome("C:\chromedriver_win32\chromedriver.exe")

    hash_from_birthdays_to_used_names = {}
    hash_from_facility_name_to_facility_id = {}

    # opening up browser
    url = "http://nysdoccslookup.doccs.ny.gov/"

    # maybe look into a more stripped down, efficient driver?
    browser.set_page_load_timeout(10)
    browser.get(url)
    # time.sleep(5)

    # searching for inmate last names with A
    browser.find_element_by_name("M00_LAST_NAMEI").send_keys("a")
    browser.find_element_by_xpath('//*[@id="il"]/form/div/div[8]/input[1]').click()  # submit button XPATH

    inmatesRemaining = True

    while(inmatesRemaining):
        source = browser.page_source
        # begin parsing html with beautiful soup
        soup = BeautifulSoup(source, 'html.parser')
        listOfTables = soup.findAll("table")
        inmateTable = listOfTables[0]  # each inmate table only gives us 4 results at most

        # The output in red at the bottom of the page
        errText = soup.find("p", {"class": "err"}).get_text()

        # where data is
        body = inmateTable.find("tbody")

        # find all rows with inmates
        listOfInmates = body.findAll("tr")  # verify row has a record!!!!

        # skip first dummy row
        for x in range(1, len(listOfInmates)):
            # time.sleep(5)
            currentRow = listOfInmates[x]
            if not checkIfWeHaveRow(hash_from_birthdays_to_used_names, currentRow, browser):
                extract(browser, x, hash_from_birthdays_to_used_names)

        print("checking if done...")
        if("NO MORE NAMES ON FILE" in errText):
            print("done!")
            inmatesRemaining = False
        else:
            print("not done!")
            browser.find_element_by_name("next").click()

    print("ending crawl")
    browser.quit()



def soupToData(soup):
    listOfTables = soup.findAll("table")
    # append all 3 tables
    listOfRows = []
    for table in listOfTables:
        # where data is
        body = table.find("tbody")
        # find all rows with inmates
        listOfRows = listOfRows + body.findAll("tr")
    return listOfRows


def extractName(data):
    # loop thru table of inmate's information
    for rows in data:
        allTd = rows.findAll('td')
        try:
            entry = allTd[0].text.strip()
            value = allTd[1].text.strip()

        except IndexError:
            # ("Not a valid table entry field")
            continue

        if entry == "Inmate Name":
            last = value.split(',')[0]
            firsts = value.split(',')[1].strip()
            fname = firsts.split(" ")[0].strip()
            try:
                mname = firsts.split(" ")[1].strip()
            except(IndexError):
                mname = ""
            lname = last.strip()
            break

    name = Name(fname, mname, lname)

    return name


def extractInmate(data):
    inmate = Inmate()
    inmate.name = extractName(data)

    # loop thru table of inmate's information
    for rows in data:
        allTd = rows.findAll('td')
        try:
            entry = allTd[0].text.strip()
            value = allTd[1].text.strip()
        except IndexError:
            # ("Not a valid table entry field")
            continue

        if entry == "Date.py of Birth":
            dob = value.split("/")
            inmate.DOB = datetime(int(dob[2]), int(dob[0]), int(dob[1]))  # year, month, day
            today = datetime.today()
            inmate.age = today.year - inmate.DOB.year - ((today.month, today.day) < (inmate.DOB.month, inmate.DOB.day))
        elif entry == "Sex":
            inmate.sex = value
        elif entry == "Race / Ethnicity":
            inmate.race = value

    return inmate



def extractFacility(data):
    facility = Facility()

    # loop thru table of inmate's information
    for rows in data:
        allTd = rows.findAll('td')
        try:
            entry = allTd[0].text.strip()
            value = allTd[1].text.strip()
        except IndexError:
            # ("Not a valid table entry field")
            continue
        if entry == "Housing / Releasing Facility":
            facility.setName(value, hash_from_facility_name_to_facility_id)

    return facility


def extractRecord(data, inmate, facility):
    record = InmateRecord()
    record.facilityID = facility.generatedID
    nextCrime = False
    # loop thru table of inmate's information
    for rows in data:
        allTd = rows.findAll('td')

        try:
            entry = allTd[0].text.strip()
            value = allTd[1].text.strip()
        except IndexError:
            # ("Not a valid table entry field")
            continue
        if nextCrime:
            nextCrime = False
            record.offense = entry
            record.offenseClass = value

        elif(value != ""):
            if entry == "DIN (Department Identification Number)":
                record.inmateNumber = value  # we should rename this to be record number
            elif entry == "Date.py Received (Current)":
                dor = value.split("/")
                if len(dor) > 1:
                    record.admissionDate = datetime(int(dor[2]), int(dor[0]), int(dor[1]))
            elif entry == "Custody Status":
                record.status = value
            elif entry == "Admission Type":
                record.admissionType = value
            elif entry == "County of Commitment":
                record.county = value
            elif entry == "Latest Release Date.py / Type (Released Inmates Only)":
                rd = value.split("/")
                rd[2] = rd[2].split()[0]
                if len(rd) > 1:
                    record.estReleaseDate = datetime(int(rd[2]), int(rd[0]), int(rd[1]))
                    record.maxReleaseDate = datetime(int(rd[2]), int(rd[0]), int(rd[1]))
            elif entry == "Conditional Release Date.py":
                erd = value.split("/")
                if len(erd) > 1:
                    record.estReleaseDate = datetime(int(erd[2]), int(erd[0]), int(erd[1]))
            elif entry == "Maximum Expiration Date.py":
                med = value.split("/")
                if len(erd) > 1:
                    record.maxReleaseDate = datetime(int(med[2]), int(med[0]), int(med[1]))
        if entry == "Latest Release Date.py / Type (Released Inmates Only)":
            # this means the next row will have the offense in entry and the offense class in value
            nextCrime = True
    inmate.addRecord(record)

    return record


def extractFirst(soup, hash_from_birthdays_to_used_names):
    data = soupToData(soup)
    inmate = extractInmate(data)
    facility = extractFacility(data)
    record = extractRecord(data, inmate, facility)

    print("FIRST!!!!!!!!!!!!")
    print(inmate)
    print(record)
    print(facility)
    hash_from_birthdays_to_used_names[inmate.DOB] = [inmate.name]
    write(inmate, record, facility)
    return inmate


def extractExtra(soup, inmate, hash_from_birthdays_to_used_names):
    data = soupToData(soup)

    name = extractName(data)
    inmate.addAlias(name)
    facility = extractFacility(data)
    record = extractRecord(data, inmate, facility)

    print("EXTRA!!!!!!!!!!!!!")
    print(inmate)
    print(record)
    print(facility)
    hash_from_birthdays_to_used_names[inmate.DOB] = hash_from_birthdays_to_used_names[inmate.DOB] + [name]


def extract(browser, rowNum, hash_from_birthdays_to_used_names):
    browser.find_element_by_name('din' + str(rowNum)).click()  # din info click
    source = browser.page_source
    soupMainPage = BeautifulSoup(source, 'html.parser')
    # check if a multi-record or single
    if isMulti(soupMainPage):
        extractMulti(browser, soupMainPage, hash_from_birthdays_to_used_names)
    else:
        extractFirst(soupMainPage, hash_from_birthdays_to_used_names)
    browser.back()


def isMulti(soup):
    try:
        if("multiple commitments" in soup.findAll('p')[1].contents[0]):
            return True
    except(IndexError):
        return False
    return False

def extractMulti(browser, soup, hash_from_birthdays_to_used_names):
    listOfTables = soup.findAll("table")
    recordTable = listOfTables[0]  # each inmate table only gives us 4 results at most

    # where data is
    body = recordTable.find("tbody")

    # find all rows with inmates
    listOfRecords = body.findAll("tr")  # verify row has a record!!!!

    browser.find_element_by_name('din1').click()
    firstSource = browser.page_source
    firstSoup = BeautifulSoup(firstSource, 'html.parser')
    inmate = extractFirst(firstSoup, hash_from_birthdays_to_used_names)  # this will save the row and return the inmate object
    browser.back()
    time.sleep(2)

    # skip first dummy row and first entry
    currentRowNum = 2
    name = "something"

    while(name != ""):
        # check record row has a name
        currentRow = listOfRecords[currentRowNum]
        cells = currentRow.findAll("td")
        parsedData = []
        # splits html row into individual elements in a list
        for cell in cells:
            parsedData += cell.contents
        try:
            name = parsedData[3].strip()  # this is a name
        except(IndexError):
            name = ""

        if (name != ""):
            # scrape row
            browser.find_element_by_name('din' + str(currentRowNum)).click()
            extraSource = browser.page_source
            extraSoup = BeautifulSoup(extraSource, 'html.parser')
            extractExtra(extraSoup, inmate, hash_from_birthdays_to_used_names)
            browser.back()
            time.sleep(2)

            # iterate movement
            currentRowNum += 1

crawl()