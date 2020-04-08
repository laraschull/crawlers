# @authors gabriel_saruhashi and benjaminsuffin
# Created at: March 11, 2020
# Last updated at: April 8, 2020

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from utils.updater import *

chrome_options = Options()
browser = webdriver.Chrome()

baseUrl = "http://www.ctinmateinfo.state.ct.us/searchop.asp"

def baseCrawler(last, first):
    # opening up browser
    browser.set_page_load_timeout(20)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    lastNameBar = "nm_inmt_last"
    browser.find_element_by_name(lastNameBar).send_keys(last)
    firstNameBar = "nm_inmt_first"
    browser.find_element_by_name(firstNameBar).send_keys(first)
    searchButton = "submit1"
    browser.find_element_by_name(searchButton).click()

    source = browser.page_source
    soup = BeautifulSoup(source, 'html.parser')
    listOfTables = soup.findAll("table")
    inmateTable = listOfTables[1]
    body = inmateTable.find("tbody")
    listOfInmates = body.findAll("tr")

    # begin parsing html with beautiful soup

    for i in range(1, len(listOfInmates) - 1):
        currentInmate = listOfInmates[i]
        cells = currentInmate.findAll("td")
        url = "http://www.ctinmateinfo.state.ct.us/" + cells[0].find('a')['href']
        browser.set_page_load_timeout(10)
        browser.get(url)

        profileSource = browser.page_source
        profileSoup = BeautifulSoup(profileSource, 'html.parser')
        name = saveInmateProfile(profileSoup, browser)

    browser.quit()


def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    record.state = "CT"
    record.status = RecordStatus.ACTIVE
    facility = Facility()
    facility.state = record.state

    listOfTables = soup.find("tbody").find('tbody')

    # loop thru table of inmate's information
    for rows in listOfTables.find_all_next("tr"):
        allTd = rows.findAll('td')

        try:
            entry = allTd[0].text.strip()
            value = allTd[1].text.strip()
        except IndexError:
            continue

        if entry == "Inmate Number:":
            record.recordNumber = value
        elif entry == "Inmate Name:":
            name = value
            lastName, firstNames = name.split(',')  # only if "last, first" order; otherwise vice versa
            firstNames = firstNames.split()
            firstName = firstNames[0]
            middleName = "" if len(firstNames[1:]) == 0 else " ".join(firstNames[1:])
            inmate.name = Name(firstName, middleName, lastName)
        elif entry == "Date of Birth:":
            inmate.DOB = Date(value)  # year, month, day
        elif entry == "Sex:":
            inmate.sex = value
        elif entry == "Race":
            inmate.race = value
        elif entry == "Current Location:":
            facility.name = value
            record.facility = facility
        elif entry == "Date of Sentence:":
            dos = value.split("/")
            if len(dos) > 1:
                record.sentenceDate = Date(value)
        elif entry == "Estimated Release Date:":
            erd = value.split("/")
            if len(erd) > 1:
                record.estReleaseDate = Date(value)
        elif entry == "Controlling Offense*:":
            record.offense = value
        elif entry == "Headshot":
            inmate.headshot = value

    inmate.addRecord(record)

    # saves profile to the database
    writeToDB(inmate)

    browser.set_page_load_timeout(10)

    return name

baseCrawler("Smith", "John")