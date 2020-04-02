from selenium import webdriver
from bs4 import NavigableString, BeautifulSoup
from models.Name import Name
import time
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord
from models.Facility import Facility
from utils.updater import *
from models.Date import Date

browser = webdriver.Chrome("chromedriver")

baseUrl = "https://www.doc.state.co.us/oss/"
client = MongoClient('localhost', 27017)
db = client.inmate_database

def baseCrawler(last, first):
    # opening up browser
    browser.set_page_load_timeout(20)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    browser.find_element_by_id("last_name").send_keys(last)
    browser.find_element_by_id("first_name").send_keys(first)
    browser.find_element_by_id("btn_search_txt").click()

    browser.implicitly_wait(5)

    nextList = True


    while nextList:
        #get list of people
        profileList = browser.find_elements_by_xpath("//*[contains(@id, 'doc_list')]")

        for i in range(len(profileList)):
            profile = profileList[i]
            browser.implicitly_wait(3)
            profile.click()
            browser.implicitly_wait(3)

            name = saveInmateProfile(browser)
            print("Done saving record with name ", name)

        nextList, button = nextButton(browser)

        if nextList is True:
            browser.find_element_by_xpath("/html/body/div[7]/div[2]/div[2]/div[2]/div[2]" + xpath_soup(button)).click()
            time.sleep(2)


    browser.quit()

def saveInmateProfile(browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    facility = Facility()

    # find inmate ID, will go in active record
    time.sleep(2)

    element = browser.find_elements_by_class_name("section_data")

    backgroundPersonInfo = BeautifulSoup(element[1].get_attribute('innerHTML'), 'html.parser').find("tbody").find("tbody")
    personInfoCells = backgroundPersonInfo.find_all("tr")

    for ind in range(len(personInfoCells)):
        cell = personInfoCells[ind]
        if not isinstance(cell, NavigableString):
            txt = " ".join(cell.text.strip().split())

            if "Name" in txt:
                fullName = txt.replace(",", "").split(" ")
                lastName = fullName[1]
                firstName = fullName[2]
                middleName = fullName[-1] if len(fullName) == 4 else None
                inmate.name = Name(firstName, middleName, lastName)
            elif "Age" in txt:
                inmate.age = txt.split(" ")[-1]
            elif "Gender" in txt:
                inmate.sex = txt.split(" ")[-1]
            elif "Ethnicity" in txt:
                inmate.race = txt.split(" ")[-1]
            elif "Hair Color" in txt:
                inmate.hairColor = txt.split(" ")[-1]
            elif "Eye Color" in txt:
                inmate.eyeColor = txt.split(" ")[-1]
            elif "Height" in txt:
                inmate.height = txt.split(" ")[-2] + txt.split(" ")[-1]
            elif "Weight" in txt:
                inmate.weight = txt.split(" ")[-1]

    backgroundPersonPrisonInfo = backgroundPersonInfo.find_next("tbody")
    personPrisonInfoCells = backgroundPersonPrisonInfo.find_all("tr")

    for ind in range(len(personPrisonInfoCells)):
        cell = personPrisonInfoCells[ind]
        if not isinstance(cell, NavigableString):
            txt = " ".join(cell.text.strip().split())

            if "DOC Number" in txt:
                # inmate's id given by Colorado Department of Corrections
                continue
            elif "Est. Parole Eligibility Date" in txt:
                dateSplit = txt.split(" ")[-1].split("/")
                if len(dateSplit) > 1:
                    record.paroleEligibilityDate = Date(dateSplit[-1], dateSplit[0], dateSplit[1])
            elif "Next Parole Hearing Date" in txt:
                dateSplit = txt.split(":")
                if len(dateSplit) > 1:
                    record.nextParoleHearingDate = dateSplit[-1].strip()
            elif "Est. Sentence Discharge Date" in txt:
                dateSplit = txt.split(" ")[-1].split("/")
                if len(dateSplit) > 1:
                    record.estReleaseDate = Date(dateSplit[-1], dateSplit[0], dateSplit[1])
            elif "Current Facility Assignment" in txt:
                facility.name = txt.split(":")[-1].strip()

    # saves profile to the database
    writeToDB(inmate)
    browser.find_element_by_id("btn_search_txt").click()
    return inmate.name.first + " " + inmate.name.last

def nextButton(browser):
    """
    finds the next button and sees if it exists
    """
    navigationButtonDiv = browser.find_element_by_xpath("/html/body/div[7]/div[2]/div[2]/div[2]/div[2]")
    spansSoup = BeautifulSoup(navigationButtonDiv.get_attribute('innerHTML'), 'html.parser')
    spansList = spansSoup.find_all("span")

    for i in spansList:
        if "NEXT" in i.text:
            return True, i
    return False

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
baseCrawler("a", "")
