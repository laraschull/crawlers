from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import NavigableString, BeautifulSoup
from models.Name import Name
from string import ascii_lowercase
from datetime import datetime
import time
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from utils.updater import *
from models.Date import Date

browser = webdriver.Chrome("chromedriver")

baseUrl = "https://doc.iowa.gov/offender/search"
client = MongoClient('localhost', 27017)
db = client.inmate_database

def baseCrawler(last, first):
    # opening up browser
    browser.set_page_load_timeout(30)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    browser.find_element_by_id("edit-last-name").send_keys(last)
    browser.find_element_by_id("edit-first-name").send_keys(first)
    browser.find_element_by_id("edit-submit-button").click()

    browser.implicitly_wait(5)

    #get list of people
    profileList = browser.find_elements_by_xpath("/html/body/div[3]/section/div/section/div[2]/form/div/table[2]"
                                                 "/tbody/tr")

    for i in range(len(profileList)):
        time.sleep(5)

        elem = browser.find_element_by_xpath("/html/body/div[3]/section/div/section/div[2]/form/div/table[2]/tbody/"
                                      "tr[" + str(i+1) + "]").find_element_by_tag_name("a")
        actions = ActionChains(browser)
        actions.move_to_element(elem).click().perform()
        browser.implicitly_wait(3)

        name = saveInmateProfile(browser)
        print("Done saving record with name ", name)



    browser.quit()

def saveInmateProfile(browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    facility = Facility()

    # find inmate ID, will go in active record
    time.sleep(10)
    try:
        element = browser.find_element_by_id("offender-information").find_elements_by_tag_name("tbody")
    except:
        return

    backgroundPersonInfo = BeautifulSoup(element[0].get_attribute('innerHTML'), 'html.parser')
    personInfoCells = backgroundPersonInfo.find_all("tr")

    for ind in range(len(personInfoCells)):
        cell = personInfoCells[ind]
        if not isinstance(cell, NavigableString):
            txt = cell.find('td').text.strip()
            value = cell.find('td').findNext('td').text.strip()
            if "Name" in txt:
                fullName = value.split(" ")
                if len(fullName) == 3:
                    lastName = fullName[-1]
                    firstName = fullName[0]
                    middleName = fullName[1]
                else:
                    lastName = fullName[-1]
                    firstName = fullName[0]
                    middleName = ""
                inmate.name = Name(firstName, middleName, lastName)
            elif "Offender Number" in txt:
                record.inmateId = value
            elif "Birth Date" in txt:
                DOB = value.split("/")
                inmate.DOB = Date(DOB[-1], DOB[0], DOB[1])
                inmate.age = int(DOB[-1]) - datetime.now().year
            elif "Sex" in txt:
                inmate.sex = value
            elif "Location" in txt:
                if len(value) != 0:
                    facility.name = value
                    facility.state = "IA"
                    record.facility = facility
            elif "Offense" in txt:
                if len(value) != 0:
                    record.offense = value
            elif "TDD/SDD" in txt:
                # TDD = Tentative Discharge Date
                # SDD = Supervision Discharge Date
                if len(value) != 0:
                    releaseDate = value.split("/")
                    record.estReleaseDate = Date(releaseDate[-1], releaseDate[0], releaseDate[1])
            elif "Commitment Date" in txt:
                if len(value) != 0:
                    admissionDate = value.split("/")
                    record.admissionDate = Date(admissionDate[-1], admissionDate[0], admissionDate[1])
            elif "Recall Date" in txt:
                if len(value) != 0:
                    paroleHearing = value.split("/")
                    record.nextParoleHearingDate = Date(paroleHearing[-1], paroleHearing[0], paroleHearing[1])
            elif "Mandatory Minimum" in txt:
                if len(value) != 0:
                    paroleEligibility = value.split("/")
                    record.paroleEligibilityDate = Date(paroleEligibility[-1], paroleEligibility[0], paroleEligibility[1])
    inmate.records = []
    record.state = "IA"
    inmate.records.append(record)

    backgroundPersonPrisonInfo = BeautifulSoup(element[1].get_attribute('innerHTML'), 'html.parser')
    personPrisonInfoCells = backgroundPersonPrisonInfo.find_all("tr")

    for ind in range(len(personPrisonInfoCells)):
        row = personPrisonInfoCells[ind]
        if not isinstance(row, NavigableString):
            newRecord = InmateRecord()
            txt = row.find_all('td')
            lst = []
            for i in txt:
                lst.append(i.text)

            newRecord.status = RecordStatus.ACTIVE
            newRecord.currentSupervisionStatus = lst[0]
            newRecord.offense = lst[1]
            newRecord.county = lst[2]
            newRecord.estReleaseDate = lst[3]
            newRecord.state = "IA"
            newRecord.inmateId = record.inmateId

            inmate.records.append(record)

    # saves profile to the database
    writeToDB(inmate)
    browser.back()
    return inmate.name.first + " " + inmate.name.last


def xpath_soup(element):
    """
    cite: https://gist.github.com/ergoithz/6cf043e3fdedd1b94fcf#gistcomment-2682315
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name
            if siblings == [child] else
            '%s[%d]' % (child.name, 1 + siblings.index(child))
        )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

"""
TESTS:
"""
# change this for a specific name search
baseCrawler("a", "")

# change this to crawl the entire database
# for s in ascii_lowercase:
#     baseCrawler(s, "")
