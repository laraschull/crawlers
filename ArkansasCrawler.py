from selenium import webdriver
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
import re
import math
from utils.updater import *

browser = webdriver.Chrome() # Jim, put extension in

baseUrl = "https://apps.ark.org/inmate_info/index.php"

def baseCrawler(last, first):
    # opening up browser
    browser.set_page_load_timeout(20)
    browser.get(baseUrl)

    # searching for inmate last names that start with certain character
    # lastNameBar = find in HTML
    browser.find_element_by_name("lastname").send_keys(last)
    # firstNameBar = find in HTML
    browser.find_element_by_name("firstname").send_keys(first)
    browser.set_page_load_timeout(10)
    # searchButton = find in HTML
    browser.find_element_by_name("disclaimer").click()
    browser.find_element_by_name("B1").click()

    # begin parsing html with beautiful soup

    source = browser.page_source
    soup = BeautifulSoup(source, 'html.parser')
    
    # profileXPath = find in HTML (path to clickable link for each person)
    
    
    numResultsList = re.sub(r'[^a-zA-Z0-9 ]', '',browser.find_element_by_xpath(
        "//*[@id='appContent']/div/center/table/tbody/tr/td/div/center/table/tbody/tr[10]/td/div/table/tbody/tr[1]/td/table/tbody/tr/td[2]/font/b/span").text).split()
    
    
    numPages = math.ceil(int(numResultsList[0])/50)
    tableLength = int(numResultsList[-1]) - int(numResultsList[-3]) + 1
    
    listOfTables = soup.findAll("table")
    inmateTable = listOfTables[1]
    inmates = (inmateTable.findAll("tr"))[9].findAll("tr")[5:5+tableLength]
    #print(inmates)
    
    profileList = []
    for i in range(len(inmates)):
        profileList.append( browser.find_elements_by_xpath(
            "//*[@id='appContent']/div/center/table/tbody/tr/td/div/center/table/tbody/tr[10]/td/div/table/tbody/tr[3]/td/table/tbody/tr[" + str(i+2) + "]/td[3]/a"))
    
    
#    for j in range(numPages):

    
    #print(profileList)

    
    
    for i in range(len(profileList)):
        
        profile = profileList[i][0]
        #print(profile.get_attribute('innerHTML'))
        browser.set_page_load_timeout(10)
        profile.click()

        soup = BeautifulSoup(browser.page_source, 'html.parser')
        name = saveInmateProfile(soup, browser)
        print(name)
        print("Done saving record with name")
        #driver.navigate().back()
    

    browser.quit()
    
    """

    while False:
        for i in range(1):

            profile = profileList[0]
            print(profile)
            browser.set_page_load_timeout(10)
            profile.click()

            soup = BeautifulSoup(browser.page_source, 'html.parser')
            name = saveInmateProfile(soup, browser)
            print("Done saving record with name ", name)

        # go to next page, if necessary
        browser.set_page_load_timeout(10)
        # nextName = find in HTML
        browser.find_element_by_id(nextName).click()

        # implement way to break loop if on the last page (ex. "next" button attribute)
        if True:
            break
    
    """


def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    record.state = "AR"
    facility = Facility()

    # idName = find in HTML
    #inmateID = soup.find(idName).get_text()  # find inmate ID, will go in active record
    name = browser.find_element_by_xpath("//*[@id='appContent']/div/center/table/tbody/tr/td/div/center/table/tbody/tr[12]/td/div/center/table/tbody/tr/td[2]/table/tbody/tr[2]/td[3]/font").text    # find inmate name
    # name = find in HTML
    # EX: name = soup.find('h4', text = re.compile('Name:.*')).get_text().strip('Name:').strip()
    #name = soup.find('tr', text = re.compile('Name:.*')).get_text().strip('Name:').strip()
    #name = soup.find("Name:").get_text()
    #print(name)
    # finds text that includes "NAME:, for example; regex"
    lastName, firstNames = name.split(',')  # only if "last, first" order; otherwise vice versa
    firstNames = firstNames.split()
    firstName = firstNames[0]
    middleName = "" if len(firstNames[1:]) == 0 else " ".join(firstNames[1:])
    inmate.name = Name(firstName, middleName, lastName)
    

    # find way to parse and collect rest of info; will vary with different crawlers

    # facility names
    facility.name = browser.find_element_by_xpath("//*[@id='appContent']/div/center/table/tbody/tr/td/div/center/table/tbody/tr[12]/td/div/center/table/tbody/tr/td[2]/table/tbody/tr[11]/td[3]/font").text
    facility.state = record.state
    #record.facilityID = facility.generatedID

    info = soup.findAll('table')
    #print(info[0])
    
    for row in info[3].findAll('tr'):
        col_num = 0
        columns = row.findAll('td')
        #print(len(columns))

        if len(columns) > 1:
            entry = columns[0].text.strip().split("\n")[0]
            entry_value = columns[2].text.strip().split("\n")[0]
            #print(entry)
            #print(len(entry))
            #print(entry_value)
            
            if entry == 'Race:':
                inmate.race = entry_value
            elif entry == 'Sex:':
                inmate.sex = entry_value
            elif entry == 'Hair Color:':
                inmate.hairColor = entry_value
            elif entry == 'Eye':
                inmate.eyeColor = entry_value
            elif entry == 'Height:':
                inmate.height = entry_value
            elif entry == 'Weight:':
                inmate.weight = entry_value
            elif entry == 'Birth Date:':
                split_DOB = entry_value.split("/")
                inmate.DOB = Date(int(split_DOB[2]), int(split_DOB[0]), int(split_DOB[1]), True)

    """
    GENERAL FORMAT: create an inmate object, add all relevant information to it. Create record object(s), fill
    in as seen fitting. Make sure mark active records as such. Call Inmate.addRecord(record) to add the record to the 
    inmate profile.
    
    Georgia example:
    
    info = soup.findAll('p')
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

    """

    # saves profile to the database
    #writeToDB(inmate)



    browser.set_page_load_timeout(10)

    # click back button
    # EX: browser.find_element_by_xpath("//a[text()=' Return to previous screen']").click()
    browser.back()
    return name

"""
TESTS:

baseCrawler(last, first)
...

"""

print(baseCrawler("anderson",""))