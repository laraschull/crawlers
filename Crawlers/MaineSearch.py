import requests
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
import re
from utils.updater import *


def baseCrawler(last, first):
    s = requests.Session()
    my_cookie = {
        "name": 'mdoc',
        "value": 'eyecolor&&status&&age_from&&order_by&mdoc_number&last_name&&mark&&inches_from&&haircolor&&weight_from&&race&&feet_to&&gender&&mejis_index&&location&&feet_from&&inches_to&&middle_name&&age_to&&weight_to&&mdoc_number&&start_limit&1&first_name&James',
        "domain": 'www1.maine.gov',
        "path": "/",
        "expires": "2020-04-10T19:10:17.178Z",
        "secure": "True",
    }
    s.cookies.set(**my_cookie)

    baseUrl = 'https://www1.maine.gov/cgi-bin/online/mdoc/search-and-deposit/results.pl?mdoc_number=&start_limit=1&status=&first_name=' + first + '&middle_name=&last_name=' + last + '&gender=&weight_from=&weight_to=&feet_from=&inches_from=&feet_to=&inches_to=&age_from=&age_to=&eyecolor=&haircolor=&race=&gender=&mejis_index=&mark=&location=&order_by=mdoc_number'
    headers = {"User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
    req = s.get(baseUrl, headers=headers)



    # begin parsing html with beautiful soup
    soup = BeautifulSoup(req.text, 'html.parser')
    print(soup)

    pagesRemaining = True

    while pagesRemaining:

        profileList = soup.find_all('a')#, href=re.compile('detail*'))
        print(profileList)
        for i in range(len(profileList)):
            profile = profileList[i]
            print(profile)
        raise SystemExit(0)

'''
            inmateUrl = ???

            inmate = saveInmateProfile(inmateUrl)

            print("Done saving record with name ", inmate.name)

        if THERE IS NO NEXT BUTTON:
            pagesRemaining = False
        else:
            nextUrl = ???
            req = requests.get(nextUrl)
            soup = BeautifulSoup(req.text, 'html.parser')



def saveInmateProfile(soup, browser):
    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    record.state = "ME"
    facility = Facility()

    # idName = find in HTML
    inmateID = soup.find(idName).get_text()  # find inmate ID, will go in active record

    # find inmate name
    # name = find in HTML
    # EX: name = soup.find('h4', text = re.compile('NAME:.*')).get_text().strip('NAME:').strip()
    # finds text that includes "NAME:, for example; regex"
    lastName, firstNames = name.split(',')  # only if "last, first" order; otherwise vice versa
    firstNames = firstNames.split()
    firstName = firstNames[0]
    middleName = "" if len(firstNames[1:]) == 0 else " ".join(firstNames[1:])
    inmate.name = Name(firstName, middleName, lastName)

    # find way to parse and collect rest of info; will vary with different crawlers

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
    writeToDB(inmate)

    browser.set_page_load_timeout(10)

    # click back button
    # EX: browser.find_element_by_xpath("//a[text()=' Return to previous screen']").click()

    return inmate

'''
baseCrawler("", "james")
