# Lara Schull
# Created at: 04/16/20
# Last updated at: 04/16/20

'''
Notes 
Omitted:
    - pid # 
    - classification
    - aliases 
    - felony class
    - last parole hearing date + action + months deferred 

'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from utils.updater import * 
# from webdriver_manager.chrome import ChromeDriverManager  
import urllib

chrome_options = Options()
chrome_options.add_argument("--headless")  # uncomment if you want chromedriver to not render
browser = webdriver.Chrome("Users/laraschull/Documents/chromedriver", options=chrome_options)  # for MAC
# browser = webdriver.Chrome("C:\chromedriver_win32\chromedriver.exe", options=chrome_options)  # for Windows
# browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options) # temp solution to PATH issues 

baseUrl = "http://kool.corrections.ky.gov/"

def baseCrawler(last, first):
    # opening up browser 
    browser.set_page_load_timeout(20)
    browser.get(baseUrl)

    # search for lastnames by initial character s
    browser.find_element_by_name("LastName").send_keys(last)
    browser.find_element_by_name("FirstName").send_keys(first)

    try:
        browser.find_element_by_name("searchButton").click()
    except: 
        print("Failed to click") # had error clicking; edit if reoccurs 
        exit()

    total = 0 
    while True:
        source = browser.page_source
        # begin parsing html with beautiful soup 
        soup = BeautifulSoup(source, 'html.parser')
        fullTable = soup.find( "table", id="searchResults")

        # get page data 
        body = fullTable.find("tbody")
        nameTable = body.findAll("tr")

        # add each profile to database, skipping row 0 (header)
        for i in range(1, len(nameTable)):
            # each profile in table is linked as href 
            offenderInfo = nameTable[i]
            tags = offenderInfo('a')
            profileURL = "http://kool.corrections.ky.gov" + tags[0].get("href")
            
            # collect HTML from profile page 
            page = urllib.request.urlopen(profileURL)
            pg_soup = BeautifulSoup(page.read(), 'html.parser')
            page.close()
            
            # format and add to table 
            saveInmateProfile(pg_soup, browser)
        
        # click through to next page of results
        try: 
            browser.find_element_by_link_text("Next >").click()
        except:
            break

    browser.quit()

def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    record.state = "KY"
    facility = Facility()
    facility.state = record.state
    record.facility = facility

    tables = soup.findAll("table")
    rows = tables[0].findAll("tr")
    aliases = tables[1]
    pastConvictions = tables[2]
    paroleInfo = tables[3]

    inmate, currentRecord = addPersonalInfo(inmate, record, rows)
    inmate = addPastConvictions(inmate, currentRecord, pastConvictions)
    inmate = addParoleInfo(inmate, paroleInfo)

    # save profile to database 
    writeToDB(inmate)
    return 

def addPersonalInfo(inmate, record, rows):

    for row in rows:
        info = row.find("div", {"class": "display-field"})

        if "Name" in str(row):
            name = info.contents[0].strip()
            lastName, firstNames = name.split(',')
            firstNames = firstNames.split() # in case middle name 
            firstName = firstNames[0]
            middleName = "" if len(firstNames[1:]) == 0 else " ".join(firstNames[1:])
            inmate.name = Name(firstName, middleName, lastName)
            # print(firstName, middleName, lastName)

            # store current incarceration status 
            status = info.find("b").contents[0]
            if "active" in str(status):
                record.status = RecordStatus.ACTIVE 
            elif "parole" in str(status):
                record.status = RecordStatus.PAROLE 
            else:
                record.status = RecordStatus.INACTIVE 
            # print(record.status)
            continue 

        value = info.contents[0].strip()

        if "PID" in str(row):
            # 2nd row = pid # and doc #
            pid, doc = value.split('/') # !! currently discarding pid: might be facility-specific ID? 
            pid = pid.strip()
            doc = doc.strip()
            record.inmateId = doc 
            # print(pid)
            # print(doc)
        
        elif "Start Date" in str(row):
            record.admissionDate = Date(value)
        
        elif "TTS" in str(row):
            tts_info = info.find("span", {"class":"dateclass"}) 
            try:
                tts_val = tts_info.contents[0].strip()
                record.estReleaseDate = Date(tts_val)
            except: 
                print("No expected sentence length found for "+str(inmate.name))
                continue 
        
        elif "Minimum Expiration" in str(row):
            try:
                record.minReleaseDate = Date(value)
            except:
                # print(inmate.name)
                # print(row)
                continue 
        
        elif "Parole Eligiblity" in str(row):
            try:
                record.paroleEligibilityDate = Date(value)
            except:
                # print(inmate.name)
                # print(row)                
                continue 
        
        elif "Maximum Expiration" in str(row):
            value = info.find("div", {"class":"display-field"})
            value = value.contents[0].strip()
            try:
                record.maxReleaseDate = Date(value)
            except:
                continue

        elif "Location" in str(row):
            record.facility.name = value

        # Record all provided personal information 
        elif "Age" in str(row):
            # KY provides only age, no DOB 
            inmate.DOB = Date(value, estimated=True) # Date constr. estimates DOB
        elif "Race" in str(row):
            inmate.race = value
        elif "Gender" in str(row):
            inmate.sex = value
        elif "Eye Color" in str(row):
            inmate.eyeColor = value 
        elif "Hair Color" in str(row):
            inmate.hairColor = value
        elif "Height" in str(row):
            inmate.height = value 
        elif "Weight" in str(row):
            inmate.weight = value 

    return inmate, record

def addPastConvictions(inmate, currentRecord, pastConvictions):
    allRecords = [currentRecord]
    recordCount = 0 
    currentRecord.offense = []
    entries = pastConvictions.findAll("tr")

    # structure: row i = header, row i+1 = details of conviction 
    # on the KY website, a single record can include multiple offenses 
    i = 0
    while i in range(0, len(entries)):
        record = allRecords[recordCount]

        header = entries[i]
        try:
            details = entries[i+1].findAll("td")
        except:
            if "Conviction information unavailable" not in header:
                print("No specific conviction info for "+ str(inmate.name))
            break 

        offense = header.findAll("th")[1].contents[0]

        lastID = None 
        lhs = details[0].contents
        for detail in lhs:
            if isinstance(detail, str):
                entry, value = detail.split(':')
                entry = entry.strip()
                value = value.strip()
            else:
                continue 
            if entry == "Indictment #":
                if not lastID or value == lastID:
                    # another offense for same conviction
                    record.offense.append(offense) # add offense to list 
                else:
                    # new conviction 
                    record = InmateRecord()
                    record.offense = [offense] # start list of related offenses 
                    lastID = value # save new indictment # 
                    recordCount += 1 # increment number of new records 
                    allRecords += [] 
        
            elif "Crime Date" in entry:
                continue
                record.crimeDate = Date(value)
            elif entry == "Conviction Date":
                try:
                    record.sentenceDate = Date(value)
                except:
                    record.sentenceDate = None 
                    continue 
            elif entry == "Conviction County":
                record.county = value

        rhs = details[1].contents
        for detail in rhs:
            try:
                entry, value = detail.split(':')
                entry = entry.strip()
                value = value.strip()
            except:
                continue 
            if entry == "KRS Code":
                record.statute = value
            elif entry == "Sentence Length":
                if not record.estReleaseDate and record.sentenceDate:
                    record.estReleaseDate = record.sentenceDate 
                    try:
                        (paramY, paramM, paramD) = [int(x.strip().split()[0]) for x in value.split(",")]
                    except(ValueError):
                        (paramY, paramM, paramD) = (None, None, None)
                    record.estReleaseDate.addTime(paramY, paramM, paramD)
                    record.estReleaseDate.estimated = True
                    record.recordNumber = lastID
            

        allRecords[recordCount] = record 
        i += 2 

    for rec in allRecords:
        inmate.addRecord(rec)

    return inmate

def addParoleInfo(inmate, paroleInfo):
    headers = paroleInfo.findAll("th")
    if len(headers) > 0:
        entries = paroleInfo.findAll("td")
        for header, entry in zip(headers, entries):
            # if "Hearing Date" in header:
            #     entry = entry.contents[0].strip()
            #     # omitted
            # elif "Hearing Action" in header:
            #     entry = entry.contents[0].strip()
            #     # omitted
            # elif "Months Deferred" in header:
            #     entry = entry.contents[0].strip()
            if "Next Parole Eligibility" in header:
                try: 
                    entry = entry.contents[0].strip()
                    inmate.records[0].paroleEligibilityDate = Date(entry)
                except:
                    continue 
            # also omitted proposed release date -- generally empty 
    return inmate 

