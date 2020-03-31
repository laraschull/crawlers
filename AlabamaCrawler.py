from selenium import webdriver
from string import ascii_lowercase
from bs4 import BeautifulSoup
from models.Inmate import Inmate
from models.InmateRecord import InmateRecord
from models.Facility import Facility
from datetime import datetime
from utils import csv_utils
from time import time
import re

browser = webdriver.Chrome('./chromedriver')
csv_utils.writeheader()

baseUrl = "http://www.doc.state.al.us/InmateSearch"

def baseCrawler(first_name, last_name):
    # opening up browser
    # maybe look into a more stripped down, efficient driver?
    browser.set_page_load_timeout(10)
    browser.get(baseUrl)
    # time.sleep(5)

    # searching for inmate last names with A
    browser.find_element_by_name("ctl00$MainContent$txtLName").send_keys(first_name)
    browser.find_element_by_name("ctl00$MainContent$txtFName").send_keys(last_name)
    browser.find_element_by_name("ctl00$MainContent$btnSearch").click()
    source = browser.page_source

    # begin parsing html with beautiful soup
    soup = BeautifulSoup(source, 'html.parser')
    listOfTables = soup.findAll("table")

    # need to start at 1 because first table is headers
    inmateTable = listOfTables[0]

    # where data is
    body = inmateTable.find("tbody")

    # find all rows with inmates
    listOfInmates = body.findAll("tr")

    # skip first dummy row

    for x in range(1, len(listOfInmates)):
        # time.sleep(5)
        currentRow = listOfInmates[x]
        inmateRowToList(currentRow, browser)

    browser.quit()

def inmateRowToList(htmlRow, browser):
    #currently still html
    cells = htmlRow.findAll("td")
    parsedData = []


    # splits html row into individual elements in a list
    for cell in cells:
        parsedData += cell.contents

    inmate = Inmate()  # inmate profile
    record = InmateRecord()  # inmate current record
    facility = Facility()

    # get inmate information
    url = "http://www.doc.state.al.us/InmateSearch" + cells[0].find('a')['href']
    browser.set_page_load_timeout(10)
    browser.get(url)

    source = browser.page_source
    soup = BeautifulSoup(source, 'html.parser')
    listOfTables = soup.find("tbody").find('tbody')

    # loop thru table of inmate's information
    for rows in listOfTables.find_all_next("tr"):
        allTd = rows.findAll('td')

        try:
            entry = allTd[0].text.strip()
            value = allTd[1].text.strip()
        except IndexError:
            print("Not a valid table entry field")
            continue

        if entry == "Inmate Number:":
            inmate.id = value
        elif entry == "Inmate Name:":
            inmate.firstNames = value.split(',')[1]
            inmate.lastName = value.split(',')[0]
        elif entry == "Birth Year":
            dob = value.split("/")
            inmate.DOB = datetime(int(dob[2]), int(dob[0]), int(dob[1])) # year, month, day
            today = datetime.today()
            # StackOverflow cite
            # https://stackoverflow.com/a/9754466
            inmate.age = today.year - inmate.DOB.year - ((today.month, today.day) < (inmate.DOB.month, inmate.DOB.day))
        elif entry == "Sex:":
            inmate.sex = value
        elif entry == "Race":
            inmate.race = value
        elif entry == "Current Location:":
            facility.name = value
        elif entry == "Date of Sentence:":
            dos = value.split("/")
            if len(dos) > 1:
                record.sentenceDate = datetime(int(dos[2]), int(dos[0]), int(dos[1]))
        elif entry == "Estimated Release Date:":
            erd = value.split("/")
            if len(erd) > 1:
                record.estReleaseDate = datetime(int(erd[2]), int(erd[0]), int(erd[1]))
        elif entry == "Controlling Offense*:":
            record.offense = value
        elif entry == "Headshot":
            inmate.headshot = value

    csv_utils.write(inmate, record, facility)
    # time.sleep(5)

baseCrawler("Amos", "")

