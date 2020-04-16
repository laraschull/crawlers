from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from models.Name import Name
from models.Date import Date
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord, RecordStatus
from models.Facility import Facility
from utils.updater import *
import math

Browser = webdriver.Chrome()

baseUrl = "http://www.dpscs.state.md.us/inmate/"
client = MongoClient('localhost', 27017)
db = client.inmate_database

def baseCrawler(last, first):
    # opening up browser
    Browser.set_page_load_timeout(100)
    Browser.get(baseUrl)

    # searching for inmate given first and last name
    Browser.find_element_by_name("lastnm").send_keys(last)
    Browser.find_element_by_name("firstnm").send_keys(first)
    Browser.find_element_by_xpath("/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr[2]/td/form/table/tbody/tr[1]/td[4]/input").click()

    # begin parsing html with beautiful soup
    soup = BeautifulSoup(Browser.page_source, 'html.parser')
    searchResults = soup.findAll("tbody")

    # gets just the first 15 results of search + total inmate number + next button
    table_of_profiles = (searchResults[4])

    # gets how much total number of results there were
    total_results = int(table_of_profiles.find_all("td", class_="smallPrint")[1].getText().split()[3])

    # each page holds up to 15 results, so finds how many pages there are in total
    number_pages = math.ceil(total_results/15)
    print("number of pages: " + str(number_pages))
    profiles = []
    # button = table_of_profiles.find_all("td", class_="smallPrint")[2].a.get('href')
    # print(button)

    for each_page in range(number_pages):
        if number_pages <= 3:
            soup = BeautifulSoup(Browser.page_source, 'html.parser')
            searchResults = soup.findAll("tbody")
            table_of_profiles = (searchResults[4])
            all_profiles = table_of_profiles.find_all('tr')[1].find_all('tr')[1:]
            print(all_profiles)
            for row in range(len(all_profiles)):
                profiles.append(all_profiles[row].a.get('href'))
            if each_page != number_pages-1:
                next_button = find_next_button(table_of_profiles, number_pages)
                print(each_page)
                print(next_button)
                Browser.get('http://www.dpscs.state.md.us' + next_button)
        else:
            soup = BeautifulSoup(Browser.page_source, 'html.parser')
            searchResults = soup.findAll("tbody")
            table_of_profiles = (searchResults[4])
            all_profiles = table_of_profiles.find_all('tr')[1].find_all('tr')[2:]
            # print(all_profiles)
            for row in range(len(all_profiles)):
                profiles.append(all_profiles[row].a.get('href'))
            if each_page != number_pages-1:
                next_button = find_next_button(table_of_profiles, each_page)
                # print(each_page)
                # print(next_button)
                Browser.get('http://www.dpscs.state.md.us' + next_button)

    print(len(profiles))

    # http://www.dpscs.state.md.us/inmate/search.do?searchType=name&firstnm=&lastnm=smith
    # http://www.dpscs.state.md.us/inmate/search.do?searchType=detail&id=301308963

    # only getting profiles that are current
    # for row in range(3, len(searchResults)):
    #     print("NEW ROW")
    #     print(searchResults[row])
        # try:
        #     profiles.append(row.a['href'])
        # except:
        #     continue
    """
    for i in range(len(profiles)):
    # for i in range(1):
        Browser.get("https://www.idoc.idaho.gov/content/prisons/offender_search/" + profiles[i])
        profilePage = BeautifulSoup(Browser.page_source, 'html.parser')
        saveInmateProfile(profilePage, Browser)
        Browser.find_element_by_xpath("//*[@id='main']/div[1]/a[4]")
    """
    Browser.quit()
def find_next_button(table_of_profiles, page_number):
    if(page_number >1):
        print(len(table_of_profiles.find_all("td", class_="smallPrint")[2].find_all("a")))
        print(table_of_profiles.find_all("td", class_="smallPrint")[2].find_all("a"))
    # if page_number > 2:
    return table_of_profiles.find_all("td", class_="smallPrint")[2].a.get('href')
    # else:
    #     return table_of_profiles.find_all("td", class_="smallPrint")[3].a.get('href')

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


baseCrawler("Lee", "")
