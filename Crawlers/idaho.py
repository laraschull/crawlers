from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from utils.updater import *

Browser = webdriver.Chrome()  # for Windows

baseUrl = "https://www.idoc.idaho.gov/content/prisons/offender_search"

def baseCrawler(last, first):
    # opening up browser
    Browser.set_page_load_timeout(100)
    Browser.get(baseUrl)

    # searching for inmate given first and last name
    Browser.find_element_by_id("offender_last_name").send_keys(last)
    Browser.find_element_by_id("offender_first_name").send_keys(first)
    Browser.find_element_by_id("edit-submit").click()

    # begin parsing html with beautiful soup
    soup = BeautifulSoup(Browser.page_source, 'html.parser')

    profiles = []

    searchResults = soup.tbody

    # only getting profiles that are current
    for row in searchResults:
        try:
            profiles.append(row.a['href'])
        except:
            continue

    # for i in range(len(profiles)):
    for i in range(1):
        Browser.get("https://www.idoc.idaho.gov/content/prisons/offender_search/" + profiles[i])
        profilePage = BeautifulSoup(Browser.page_source, 'html.parser')
        saveInmateProfile(profilePage, Browser)
    Browser.quit()

# https://www.idoc.idaho.gov/content/prisons/offender_search/


def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    record.state = "Idaho"
    # record.status = (RecordStatus.ACTIVE,INACTIVE)
    facility = Facility()
    facility.state = record.state

    # idName = find in HTML
    # inmateID = soup.find(idName).get_text()  # find inmate ID, will go in active record

    # find name in html
    name = soup.th.get_text().split()

    firstName = name[0]

    # check if middle name exists or not
    if len(name) == 4:
        middleName = name[1]
        lastName = name[2]
    else:
        middleName = ""
        lastName = name[1]

    inmate.name = Name(firstName, middleName, lastName)
    print("NAME: " + str(inmate.name))

    # set record status
    record.status = RecordStatus.ACTIVE

    # record.recordNumber = case_number

    # IDOC number assigned as inmate number
    record.inmateNumber = name[-1].split("#")[1]

    all_tables = soup.find_all("tbody")
    place_info = all_tables[0]

    for row in place_info:
        try:
            # remove extra formatting like spaces/tabs
            whole_line = ' '.join(row.get_text().split())

            # get rid of mailing address: label
            remove_address_label = whole_line.split("Mailing Address: ")

            # split address and age
            isolate_institution = remove_address_label[1].split("Status: Age: Inmate ")
            facility.name = isolate_institution[0]

            # estimate date based on age

            # inmate.DOB = Date.ageToDate(Date(int(isolate_institution[1]), True))
        except:
            continue

    charge_info = all_tables[2].find_all("td")
    print("THIS IS THEIR OFFENSE")
    for row in charge_info:
        try:
            print((' '.join(row.get_text().split())))
        except:
            continue

    # inmate.addRecord(record)
    # saves profile to the database
    # writeToDB(inmate)
    #
    # browser.set_page_load_timeout(10)
    #
    # # click back button
    # # EX: browser.find_element_by_xpath("//a[text()=' Return to previous screen']").click()

    return inmate.name


baseCrawler("Smith", "John")
