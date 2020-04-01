from selenium import webdriver
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
import re
# from utils.updater import *

browser = webdriver.Chrome()  # Jim, put extension in

baseUrl = "http://www.doc.state.al.us/InmateSearch"
# baseUrl =


def baseCrawler(last_name, first_name):
    # opening up browser
    browser.set_page_load_timeout(20)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    browser.find_element_by_name("ctl00$MainContent$txtFName").send_keys(first_name)
    browser.find_element_by_name("ctl00$MainContent$txtLName").send_keys(last_name)

    # click search button
    browser.find_element_by_name("ctl00$MainContent$btnSearch").click()

    # begin parsing html with beautiful soup
    # profileXPath = find in HTML (path to clickable link for each person)

    # if next page exists (by checking to see if the next page arrow exists, see how many pages there are
    try:
        browser.find_element_by_id("MainContent_gvInmateResults_btnNext")
        numPages = int(browser.find_element_by_id("MainContent_gvInmateResults_lblPages").text)
    except NameError:
        # if next page button doesn't exist, there is only one page of results
        numPages = 1


    profileList = []
    tableLength = int(browser.find_element_by_id("MainContent_lblMessage").text.split()[3])
    for i in range(tableLength):
        profileList.append(browser.find_elements_by_xpath("//*[@id='MainContent_gvInmateResults_lnkInmateName_" + str(i) + "']")[0])

    for j in range(numPages):
        # for i in range(len(profileList)):
        for i in range(1):
            profile = profileList[i]
            browser.set_page_load_timeout(10)
            profile.click()
            # SOMEHOW GO BACK TO ORIGINAL SEARCH PAGE

            soup = BeautifulSoup(browser.page_source, 'html.parser')
            print(soup)
            name = saveInmateProfile(soup, browser)
            print("Done saving record of", name)
            # browser.quit()
        if numPages != 1:
            if int(browser.find_element_by_id("MainContent_gvInmateResults_lblCurrent").text) != numPages:
                # go to next page, if necessary
                browser.set_page_load_timeout(10)
                # next button = find in HTML
                browser.find_element_by_id("MainContent_gvInmateResults_btnNext").click()

    browser.quit()


def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    # record.state = "XX"
    facility = Facility()

    # idName = find in HTML
    inmateID = soup.find(id="MainContent_DetailsView2_Label2").get_text()  # find inmate ID, will go in active record

    # find inmate name
    # name = find in HTML
    # EX: name = soup.find('h4', text = re.compile('NAME:.*')).get_text().strip('NAME:').strip()
    # finds text that includes "NAME:, for example; regex"
    name = soup.find(id="MainContent_DetailsView2_Label1").get_text()
    lastName, firstNames = name.split(',')  # only if "last, first" order; otherwise vice versa
    firstNames = firstNames.split()
    firstName = firstNames[0]
    middleName = "" if len(firstNames[1:]) == 0 else " ".join(firstNames[1:])
    inmate.name = Name(firstName, middleName, lastName)

    # find way to parse and collect rest of info; will vary with different crawlers

    #Georgia example:

    info = soup.findAll('td')
    print(info)
    caseNumbers = [x.text.strip('CASE NO:').strip() for x in soup.findAll('h7')]
    recordCounter = 0
    for row in info:
        if row and 'class="offender"' in str(row):
            data = row.text.split('\n')
            data = map(str.strip, data)
            data = list(filter(None, data))

            # past convictions
            if any("SENTENCE LENGTH" in s for s in data):

                for info in data:
                    try:
                        entry, value = info.split(': ')
                    except:
                        continue
                    if entry == 'OFFENSE':
                        past_record = InmateRecord()
                        past_record.inmateNumber = inmateID
                        past_record.status = RecordStatus.INACTIVE
                        past_record.state = "GA"
                        past_record.offense = value
                    elif entry == 'CRIME COMMIT DATE':
                        past_record.sentenceDate = Date(value)
                    elif entry == 'SENTENCE LENGTH':
                        past_record.estReleaseDate = past_record.sentenceDate
                        try:
                            (paramY, paramM, paramD) = [int(x.strip().split()[0]) for x in value.split(",")]
                        except(ValueError):
                            (paramY, paramM, paramD) = (None, None, None)
                        past_record.estReleaseDate.addTime(paramY, paramM, paramD)
                        past_record.estReleaseDate.estimated = True
                        past_record.recordNumber = caseNumbers[recordCounter]
                        inmate.addRecord(past_record)
                        recordCounter += 1

            # information about current conviction
            else:
                for trait in data:
                    try:
                        entry, value = trait.split(': ')
                    except:
                        continue
                    if entry == 'RACE':
                        inmate.race = value
                    elif entry == 'GENDER':
                        inmate.sex = value
                    elif entry == 'HEIGHT':
                        inmate.height = value
                    elif entry == 'EYE COLOR':
                        inmate.eyeColor = value
                    elif entry == 'YOB':
                        inmate.DOB = Date(value)
                    elif entry == 'WEIGHT':
                        inmate.weight = value
                    elif entry == 'HAIR COLOR':
                        inmate.hairColor = value
                    elif entry == 'MOST RECENT INSTITUTION':
                        facility.name = value
                        facility.state = record.state
                        record.addFacility(facility)
                    elif entry == 'MAX POSSIBLE RELEASE DATE':
                        record.maxReleaseDate = Date(value)
                        record.status = RecordStatus.ACTIVE
            record.recordNumber = caseNumbers[0]
            record.status = RecordStatus.ACTIVE
            record.inmateNumber = inmateID
            inmate.addRecord(record)


    # saves profile to the database
    # writeToDB(inmate)

    browser.set_page_load_timeout(10)

    # click back button
    # EX: browser.find_element_by_xpath("//a[text()=' Return to previous screen']").click()

    return name
#
#
# """
# TESTS:
#
# baseCrawler(last, first)
# ...
#
# """
baseCrawler("Adams", "")