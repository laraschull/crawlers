# @author benjaminsuffin
# Created at: March 29, 2020
# Last updated at: April 8, 2020

from selenium import webdriver
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from utils.updater import *

browser = webdriver.Chrome()

baseUrl = "http://www.dc.state.fl.us/OffenderSearch/Search.aspx?TypeSearch=AI"

def baseCrawler(last, first):
    # opening up browser
    browser.set_page_load_timeout(20)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    aliasCheckMark = "ctl00$ContentPlaceHolder1$chkSearchaliases"
    browser.find_element_by_name(aliasCheckMark).click()  # turn off aliases
    lastNameBar = "ctl00$ContentPlaceHolder1$txtLastName"
    browser.find_element_by_name(lastNameBar).send_keys(last)
    firstNameBar = "ctl00$ContentPlaceHolder1$txtFirstName"
    browser.find_element_by_name(firstNameBar).send_keys(first)
    searchButton = "ctl00$ContentPlaceHolder1$btnSubmit1"
    browser.find_element_by_name(searchButton).click()
    firstInmateXPath = "// *[ @ id = 'ctl00_ContentPlaceHolder1_grdList'] / tbody / tr[2] / td[2] / a"
    browser.find_element_by_xpath(firstInmateXPath).click()

    while True:

        soup = BeautifulSoup(browser.page_source, 'html.parser')
        saveInmateProfile(soup, browser)
        browser.set_page_load_timeout(10)

        nextName = "ctl00$ContentPlaceHolder1$btnDetailNext"
        nextButton = browser.find_element_by_name(nextName)
        # if last page, break loop; else, continue to next page
        if nextButton.get_attribute("disabled") == "true":
            break
        else:
            nextButton.click()
            browser.set_page_load_timeout(10)


    browser.quit()

def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    record.status = RecordStatus.ACTIVE
    record.state = "FL"
    facility = Facility()
    facility.state = record.state
    inmate.headshot = browser.find_element_by_id("ctl00_ContentPlaceHolder1_imgPhoto").get_attribute("src")
    infoTable = soup.findAll("td")
    record.recordNumber = infoTable[0].text
    fullName = infoTable[1].text
    lastName, firstNames = fullName.split(',')  # only if "last, first" order; otherwise vice versa
    firstNames = firstNames.split()
    firstName = firstNames[0]
    middleName = "" if len(firstNames[1:]) == 0 else " ".join(firstNames[1:])
    inmate.name = Name(firstName, middleName, lastName)
    inmate.race = infoTable[2].text
    inmate.sex = infoTable[3].text
    inmate.DOB = Date(infoTable[4].text)
    record.admissionDate = Date(infoTable[5].text)
    facility.name = infoTable[6].text
    record.facility = facility
    releaseDate = infoTable[8].text
    if releaseDate == " SENTENCED TO LIFE":
        record.estReleaseDate = Date("12/31/9999")
    else:
        record.estReleaseDate = Date(infoTable[8].text)

    inmate.addRecord(record)
    # saves profile to the database
    writeToDB(inmate)
    return inmate.name


