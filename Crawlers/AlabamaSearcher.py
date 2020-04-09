from selenium import webdriver
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from utils.updater import *
"""
Alabama Crawler currently:

has implemented:
-entering given first/last name into alabama website and getting a list of search results
-saves xpath of all profiles from search results as a list
-goes into list and goes to first profile
-correctly gets current information (name/age/sex/hair color/eye color/height/race/current facility name)

needs to implement:
- save current arrest details (current site is pretty unfriendly for parsing info, e.g. some attributes
are combined with each other in html like SUF and Admit date)
- saving past records (some prisoners include past records in profile)
- a way to access original list of search results (once a profile is accessed
the original results list cannot be accessed again

possible solution: 
-start the search again after every profile access
-open a tab for the number of results of the search results list url and go into different profiles in each tab

"""
browser = webdriver.Chrome()
baseUrl = "http://www.doc.state.al.us/InmateSearch"


def baseCrawler(last_name, first_name):

    # opening up browser
    browser.set_page_load_timeout(20)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    browser.find_element_by_name("ctl00$MainContent$txtFName").send_keys(first_name)
    browser.find_element_by_name("ctl00$MainContent$txtLName").send_keys(last_name)

    # click search button
    browser.find_element_by_name("ctl00$MainContent$btnSearch").click()

    # if next page exists (by checking to see if the next page arrow exists, see how many pages there are
    try:
        browser.find_element_by_id("MainContent_gvInmateResults_btnNext")
        numPages = int(browser.find_element_by_id("MainContent_gvInmateResults_lblPages").text)
    except NameError:
        # if next page button doesn't exist, there is only one page of results
        numPages = 1


    profileList = []
    tableLength = int(browser.find_element_by_id("MainContent_lblMessage").text.split()[3])

    # list of links to get to different profiles
    for i in range(tableLength):
        profileList.append(browser.find_elements_by_xpath("//*[@id='MainContent_gvInmateResults_lnkInmateName_" + str(i) + "']")[0])


    for j in range(numPages):
        for i in range(len(profileList)):
            profile = profileList[i]
            browser.set_page_load_timeout(10)
            profile.click()

            soup = BeautifulSoup(browser.page_source, 'html.parser')
            name = saveInmateProfile(soup, browser)
            print("Done saving record of", name)
            # browser.quit()

        """ Below is currently throwing error, because no way to get to other profiles currently """
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
    record.state = "Alabama"
    facility = Facility()   # current facility info

    # inmate id specific to alabama
    inmateID = soup.find(id="MainContent_DetailsView2_Label2").get_text()

    # find name element
    name = soup.find(id="MainContent_DetailsView2_Label1").get_text()
    lastName, firstNames = name.split(',')
    firstNames = firstNames.split()
    firstName = firstNames[0]
    middleName = "" if len(firstNames[1:]) == 0 else " ".join(firstNames[1:])

    # add name to inmate object
    inmate.name = Name(firstName, middleName, lastName)

    # get info off profile pages
    info = soup.findAll('table')

    # facility names
    facility.name = info[0].find(id="MainContent_DetailsView2_Label3").get_text()
    facility.state = record.state
    # record.facilityID = facility.generatedID

    # recordCounter = 0

    for i in range(1, len(info)):
        count = 0
        for row in info[i]:
            # skip first dummy row
            if count != 1:
                count += 1
            else:
                currentRecord = False
                for trait in row:
                    if i == 1:
                        try:
                            lines = trait.text.split("\n")
                            traits = lines[1].split(":")
                        except AttributeError:
                            continue
                        if traits[0] == "Race":
                            inmate.race = traits[1]
                        elif traits[0] == "Sex":
                            inmate.sex = traits[1]
                        elif traits[0] == "Hair Color":
                            inmate.hairColor = traits[1]
                        elif traits[0] == "Eye Color":
                            inmate.eyeColor = traits[1]
                        elif traits[0] == "Height":
                            inmate.height = traits[1]
                        elif traits[0] == "Birth Year":
                            inmate.DOB = Date(traits[1], None, None, True)
                        elif traits[0] == "Sex":
                            inmate.sex = traits[1]
                    elif i == 2:
                        # print('NEW ROW')
                        # print(trait)
                        try:
                            lines = trait.text.split("\n")
                            traits = lines[1].split(" ")
                            print(traits)
                        except AttributeError:
                            continue


    # save profile to the database
    writeToDB(inmate)

    browser.set_page_load_timeout(10)

    # need way to get back to original search list results
    # EX: browser.find_element_by_xpath("//a[text()=' Return to previous screen']").click()

    return name

# TESTS:
# baseCrawler("Adams", "")