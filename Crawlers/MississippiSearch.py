# @author Nikhil
# Created at: 4/9/20
# Last updated at: 4/14/20

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
# chrome_options.add_argument("--headless")  # uncomment if you want chromedriver to not render
browser = webdriver.Chrome("../chromedriver", options=chrome_options)  # for MAC
# browser = webdriver.Chrome("C:\chromedriver_win32\chromedriver.exe", options=chrome_options)  # for Windows

baseUrl = "https://www.ms.gov/mdoc/inmate"

def baseCrawler(last, first):
    # opening up browser
    browser.set_page_load_timeout(20)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    lastNameBar = "LastName"
    browser.find_element_by_name(lastNameBar).send_keys(last)
    firstNameBar = "FirstName"
    browser.find_element_by_name(firstNameBar).send_keys(first)
    browser.set_page_load_timeout(10)
    searchButton = browser.find_element_by_xpath("//input[@value='SEARCH >>']")
    searchButton.click()

    # begin parsing html with beautiful soup

    while True:
        profileXPath = "//a[@class='golink']"
        profileList = browser.find_elements_by_xpath(profileXPath)
        for i in range(len(profileList)):
            profile = browser.find_elements_by_xpath(profileXPath)[i]
            browser.set_page_load_timeout(10)
            profile.click()

            soup = BeautifulSoup(browser.page_source, 'html.parser')
            name = saveInmateProfile(soup, browser)
            print("Done saving record with name " + name.last + ", " + name.first)

        # go to next page, if necessary
        browser.set_page_load_timeout(10)
        # nextName = find in HTML
        browser.find_element_by_id(nextName).click()

        # implement way to break loop if on the last page (ex. "next" button attribute)
        nextButton = "NextPageButton"
        nextButtonElement = broswer.find_element_by_id(nextButtonId)
        lastPage = nextButtonElement.get("class") == "disabled"
        if lastPage:
            # no next page, break
            break
        else:
            # go to next page
            browser.find_element_by_id(nextButton).click()

    browser.quit()


def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    record.status = RecordStatus.ACTIVE
    record.state = "MS"
    # record.status = (RecordStatus.ACTIVE,INACTIVE)
    facility = Facility()
    facility.state = record.state

    inmateID = soup.find('h4', attrs={"class": "inmateID"}).get_text().strip().split()[-1]  # find inmate ID, will go in active record

    # find inmate name
    name =  soup.find('div', attrs={"class": "span8"}).find('h3').get_text().strip()
    # finds text that includes "NAME:, for example; regex"
    firstNames, lastName = name.split()  # only if "last, first" order; otherwise vice versa
    firstNames = firstNames.split()
    firstName = firstNames[0]
    middleName = "" if len(firstNames[1:]) == 0 else " ".join(firstNames[1:])
    inmate.name = Name(firstName, middleName, lastName)

    # find way to parse and collect rest of info; will vary with different crawlers
    table = soup.find('table', attrs={"class": "table table-striped"}).find('tbody')
    cells = table.find_all('td')
    for cell in cells:
        try:
            entry, value = cell.get_text().split(': ')
        except:
            continue
        if entry == 'Race':
            inmate.race = value
        elif entry == 'Sex':
            inmate.sex = value
        elif entry == 'Height':
            inmate.height = value
        elif entry == 'Eye Color':
            inmate.eyeColor = value
        elif entry == 'Date of Birth':
            inmate.DOB = Date(value)
        elif entry == 'Weight':
            inmate.weight = value
        elif entry == 'Hair Color':
            inmate.hairColor = value
        elif entry == 'Entry Date':
            record.admissionDate = Date(value)
            record.maxReleaseDate = Date(value)
        elif entry == 'Total Length':
            try:
                (paramY, paramM, paramD) = (0, 0, 0)
                for x in value.split(","):
                    if x.strip().split()[1] == 'YEARS':
                        paramY = int(x.strip().split()[0])
                    elif x.strip().split()[1] == 'MONTHS':
                        paramM = int(x.strip().split()[0])
                    elif x.strip().split()[1] == 'DAYS':
                        paramD = int(x.strip().split()[0])
            except(ValueError):
                (paramY, paramM, paramD) = (None, None, None)
            record.maxReleaseDate.addTime(paramY, paramM, paramD)
            record.maxReleaseDate.estimated = True
        elif entry == 'Location':
            #for Early Release Supervision status
            if value.strip().split()[-1] == "SUPERVISION":
                facility.parole = True
                record.status = RecordStatus.PAROLE
            facility.name = value
            facility.getGeneratedID()
            facility.state = record.state
            record.addFacility(facility)

    #storing offenses
    h4s = soup.find('div', attrs={"class": "span8"}).find_all('h4')
    offenses = []
    for h4 in h4s:
        if h4.get_text().strip().split()[0] == 'OFFENSE':
            offenses.append(h4.get_text().strip().split(':')[-1])
    record.offenses = offenses

    #storing estimated release date
    div_tables = soup.find('div', attrs={"class": "span8"}).find_all('table')
    for table in div_tables:
        rows = table.find('tbody').find_all('tr')
        if len(rows) == 1:
            cells = table.find_all('td')
            if len(cells) == 1:
                try:
                    entry, value = cells[0].get_text().split(':')
                except:
                    continue
                if entry == 'Tentative Release':
                    record.estReleaseDate = Date(value)

    record.inmateId = inmateID
    inmate.addRecord(record)
    # saves profile to the database
    writeToDB(inmate)

    browser.set_page_load_timeout(10)

    # click back button
    # EX: browser.find_element_by_xpath("//a[text()=' Return to previous screen']").click()
    return inmate.name