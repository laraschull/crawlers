from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
import re
from utils.updater import *

baseUrl = "https://www1.maine.gov/cgi-bin/online/mdoc/search-and-deposit/search.pl?Search=Continue"

def baseCrawler(last, first):
    # opening up browser
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # uncomment if you want chromedriver to not render
    # browser = webdriver.Chrome(".\chromedriver", options=chrome_options)  # for MAC
    browser = webdriver.Chrome("C:\chromedriver_win32\chromedriver.exe", options=chrome_options)  # for Windows

    browser.set_page_load_timeout(20)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    lastNameBar = "last_name"
    browser.find_element_by_name(lastNameBar).send_keys(last)
    firstNameBar = "first_name"
    browser.find_element_by_name(firstNameBar).send_keys(first)
    browser.set_page_load_timeout(10)
    searchButton = "submit"
    browser.find_element_by_name(searchButton).click()

    # begin parsing html with beautiful soup
    morePages = True
    while morePages:
        profileXPath = "//a[contains(@href,'detail')]"
        profileList = browser.find_elements_by_xpath(profileXPath)[0::2]
        for i in range(len(profileList)):
            profile = browser.find_elements_by_xpath(profileXPath)[0::2][i]
            browser.set_page_load_timeout(10)
            profile.click()

            soup = BeautifulSoup(browser.page_source, 'html.parser')
            inmate = saveInmateProfile(soup, browser)
            print("Done saving record with name ", inmate.name)

        # go to next page, if necessary
        browser.set_page_load_timeout(10)
        # nextName = find in HTML
        try:
            browser.find_element_by_xpath("//*[contains(text(), 'Next 30 results')]").click()
        except(NoSuchElementException):
            morePages = False

    browser.quit()


def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    record.state = "ME"
    facility = Facility()
    facility.state = "ME"

    # find way to parse and collect rest of info; will vary with different crawlers
    tables = soup.findAll('table')
    inmateTable = tables[4]

    for row in inmateTable.findAll("tr"):
    # loop thru table of inmate's information
        allTd = row.findAll('td')

        try:
            entry = allTd[0].text.strip()
            value = allTd[1].text.strip()
        except IndexError:
            print("Not a valid table entry field")
            continue
        print(entry, value)
        if entry == "MDOC Number:":
            record.inmateNumber = value
        elif entry == "Last Name, First Name, Middle Initial:":
            inmate.name = Name.getByLFM(value)
        elif entry == "Date of Birth:":
            dob = value.split("/")
            inmate.DOB = Date(int(dob[2]), int(dob[0]), int(dob[1]))  # year, month, day
        elif entry == "Gender:":
            inmate.sex = value
        elif entry == "Race/Ethnicity:":
            inmate.race = value
        elif entry == "Eye Color:":
            inmate.eyeColor = value
        elif entry == "Height:":
            inmate.height = value
        elif entry == "Weight (Pounds):":
            inmate.weight = value
        elif entry == "Hair Color:":
            inmate.hairColor = value
        elif entry == "Current Location:":
            facility.name = value
        elif entry == "Date of Sentence:":
            dos = value.split("/")
            if len(dos) > 1:
                record.sentenceDate = Date(int(dos[2]), int(dos[0]), int(dos[1]))
        elif entry == "Estimated Release Date:":
            erd = value.split("/")
            if len(erd) > 1:
                record.estReleaseDate = Date(int(erd[2]), int(erd[0]), int(erd[1]))
        elif entry == "Controlling Offense*:":
            record.offense = value
        elif entry == "Headshot":
            inmate.headshot = value


    # saves profile to the database
    writeToDB(inmate)

    browser.set_page_load_timeout(10)

    # click back button
    browser.find_element_by_xpath("//input[@value='Back to Search Results']").click()

    return inmate


baseCrawler("", "ran")