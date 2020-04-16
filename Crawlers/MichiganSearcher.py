from selenium import webdriver
import re
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import NavigableString, BeautifulSoup
from models.Name import Name
import time
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from utils.updater import *
from models.Date import Date

browser = webdriver.Chrome("chromedriver")

baseUrl = "http://mdocweb.state.mi.us/OTIS2/otis2.aspx"
client = MongoClient('localhost', 27017)
db = client.inmate_database

def baseCrawler(last, first):
    # opening up browser
    browser.set_page_load_timeout(10)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    browser.find_element_by_id("txtboxLName").send_keys(last)
    browser.find_element_by_id("txtboxFName").send_keys(first)
    browser.find_element_by_id("btnSearch").click()

    browser.implicitly_wait(5)

    # get list of people
    profileList = browser.find_elements_by_class_name("offenderRow")

    for i in range(len(profileList)):
        time.sleep(5)

        elem = browser.find_element_by_xpath("/html/body/form/div/div[" + str(i + 3) + "]")\
            .find_element_by_class_name("btnLink")
        actions = ActionChains(browser)
        actions.move_to_element(elem).click().perform()

        name = saveInmateProfile(browser)
        print("Done saving record with name ", name)



    browser.quit()

def saveInmateProfile(browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    facility = Facility()

    # find inmate ID, will go in active record
    browser.implicitly_wait(3)


    backgroundPersonInfo = BeautifulSoup(browser.find_element_by_id("pnlResults").get_attribute('innerHTML'),
                                         'html.parser')
    recordNumber = str(backgroundPersonInfo.find(id="valOffenderNumber").string)
    record.recordNumber = recordNumber
    name = str(backgroundPersonInfo.find(id="valFullName").string).strip().split(" ")
    if len(name) == 3:
        inmate.name = Name(name[0], name[1], name[2])
    else:
        inmate.name = Name(name[0], "", name[2])
    inmate.race = str(backgroundPersonInfo.find(id="valRace").string)
    inmate.sex = str(backgroundPersonInfo.find(id="valGender").string)
    inmate.hairColor = str(backgroundPersonInfo.find(id="valHairColor").string)
    inmate.eyeColor = str(backgroundPersonInfo.find(id="valEyeColor").string)
    inmate.height = str(backgroundPersonInfo.find(id="valHeight").string)
    inmate.weight = str(backgroundPersonInfo.find(id="valWeight").string)
    DOB = list(filter(None, re.sub("\D", "/", backgroundPersonInfo.find(id="valBirthDate").string).split("/")))
    inmate.DOB = Date(DOB[2], DOB[0], DOB[1])
    inmate.headshot = "http://mdocweb.state.mi.us/OTIS2/" + str(backgroundPersonInfo.find(id="imgOffender")['src'])


    currentStatus = BeautifulSoup(browser.find_element_by_id("pnlStatusAlias").get_attribute('innerHTML'),
                                  'html.parser')
    record.status = RecordStatus.ACTIVE
    facility.name = str(currentStatus.find(id='valLocation').string)
    facility.state = "MA"
    record.facility = facility
    estReleaseDate = str(currentStatus.find(id='valEarliestReleaseDate').string).split("/")
    if len(estReleaseDate) == 3:
        record.estReleaseDate = Date(estReleaseDate[2], estReleaseDate[0], estReleaseDate[1])
    maxReleaseDate = str(currentStatus.find(id='valDischargeDate').string)
    if len(maxReleaseDate) == 3:
        record.maxReleaseDate = Date(maxReleaseDate[2], maxReleaseDate[0], maxReleaseDate[1])
    record.state = "MI"
    inmate.addRecord(record)


    activePrisonSentences = BeautifulSoup(browser.find_element_by_id("pnlPASentences").get_attribute('innerHTML'),
                                          'html.parser')
    extractSoup(inmate, activePrisonSentences, 1, recordNumber)

    inactivePrisonSentences = BeautifulSoup(browser.find_element_by_id("pnlPISentences").get_attribute('innerHTML'),
                                            'html.parser')
    extractSoup(inmate, inactivePrisonSentences, 0, recordNumber)


    activeProbationSentences = BeautifulSoup(browser.find_element_by_id("pnlRASentences").get_attribute('innerHTML'),
                                             'html.parser')
    extractSoup(inmate, activeProbationSentences, 2, recordNumber)


    inactiveProbationSentences = BeautifulSoup(browser.find_element_by_id("pnlRISentences").get_attribute('innerHTML'),
                                            'html.parser')
    extractSoup(inmate, inactiveProbationSentences, 0, recordNumber)


    # saves profile to the database
    writeToDB(inmate)
    browser.back()
    return inmate.name.first + " " + inmate.name.last

def extractSoup(inmate, soup, recordStatus, recordNumber):
    record = InmateRecord()
    for child in soup.findChildren("div"):
        text = child.text
        if not isinstance(child.next_sibling, NavigableString):
            childText = child.next_sibling.text.strip()
            if "Sentence" in text:
                if record.state is not None and record.recordNumber is not None and record.dateOfOffense is not None\
                        and record.county is not None:
                    inmate.addRecord(record)
                    record = InmateRecord()
                    record.status = RecordStatus(recordStatus)
                    record.state = "MI"
                    record.recordNumber = recordNumber
            elif "Offense" in text:
                record.offense = childText
            elif "Date of Offense" in text:
                DOF = childText.split("/")
                record.dateOfOffense = Date(DOF[2], DOF[0], DOF[1])
            elif "County" in text:
                record.county = childText
    if record.state is not None and record.recordNumber is not None:
        inmate.addRecord(record)

"""
TESTS:
"""
# change this for a specific name search
baseCrawler("abrams", "")

# change this to crawl the entire database
# this website needs whole last name to get person
# for s in ascii_lowercase:
#     baseCrawler(s, "")
