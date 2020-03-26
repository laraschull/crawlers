from selenium import webdriver
from string import ascii_lowercase
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from datetime import datetime
from utils import csv_utils
import time
import re
from pymongo import MongoClient
from utils.identifier import *
from utils.updater import *

browser = webdriver.Chrome("C:\chromedriver_win32\chromedriver.exe")
csv_utils.writeheader()

baseUrl = "http://www.dcor.state.ga.us/GDC/OffenderQuery/jsp/OffQryForm.jsp?Institution="
client = MongoClient('localhost', 27017)
db = client.inmate_database

def baseCrawler():
    # opening up browser
    browser.set_page_load_timeout(20)
    browser.get(baseUrl)
    
    # get past info page
    browser.find_element_by_name("submit2").click()
    for s in ascii_lowercase:

        print("Scraping inmate records whose last name start with {}".format(s.upper()))
        
        # searching for inmate last names that start with certain character
        browser.find_element_by_name("vLastName").send_keys(s)
        browser.set_page_load_timeout(10)
        browser.find_element_by_name("NextButton2").click()

        # begin parsing html with beautiful soup
        num_profiles = len(browser.find_elements_by_xpath("//input[@value='View Offender Info']"))
        pages = browser.find_element_by_xpath("//span[@class='oq-nav-btwn']").text.split('of ')[-1]
        
        for v in range(0, int(pages)): 
            for i in range(0, num_profiles):

                profile = browser.find_elements_by_xpath("//input[@value='View Offender Info']")[i]
                browser.set_page_load_timeout(10)
                profile.click()

                soup = BeautifulSoup(browser.page_source, 'html.parser')
                name = saveInmateProfile(soup, browser)
                print("PAGE {}: Done saving record {}/{}: {}".format(v, i, num_profiles, name))
            
            # go to next page
            browser.set_page_load_timeout(10)
            browser.find_element_by_id('oq-nav-nxt').click()
        
        # return to home page for the next character
        back_btn = browser.find_element_by_xpath("//span[text()='Start a New Search']")
        back_btn.find_element_by_xpath('..').click()

    browser.quit()

def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    record.state = "GA"
    facility = Facility()

    inmateID = soup.find('h5', text = re.compile('GDC ID:.*')).get_text().strip().split()[-1]
    
    name = soup.find('h4', text = re.compile('NAME:.*')).get_text().strip('NAME:').strip()
    lastName, firstNames = name.split(',')
    firstNames = firstNames.split()
    firstName = firstNames[0]
    middleName = "" if len(firstNames[1:]) == 0 else " ".join(firstNames[1:])
    inmate.name = Name(firstName, middleName, lastName)
    

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
                        #record.addFacility(facility)
                    elif entry == 'MAX POSSIBLE RELEASE DATE':
                        record.maxReleaseDate = Date(value)
                        record.status = RecordStatus.ACTIVE
            record.recordNumber = caseNumbers[0]
            record.status = RecordStatus.ACTIVE
            record.inmateNumber = inmateID
            inmate.addRecord(record)

    if(db.inmates.count_documents({"_id": generate_inmate_id(inmate)}) == 0):  # insert new inmate
        print("new inmate")
        db.inmates.insert_one(inmate.getDict())
    else:  # update existing inmate
        print("repeat inmate")
        updateInmate(inmate)  # from utils.updater

    for rec in inmate.records:
        if (db.records.count_documents({"_id": rec.getGeneratedID()}) == 0):  # insert new record
            print("new record")
            db.records.insert_one(rec.getDict())
        else:  # update existing record
            print("repeat record")
            updateRecord(record)  # from utils.updater



    browser.set_page_load_timeout(10)
    browser.find_element_by_xpath("//a[text()=' Return to previous screen']").click()

    return name

baseCrawler()
