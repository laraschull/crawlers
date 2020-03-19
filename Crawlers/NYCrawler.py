import sys
sys.path.append("..")

from selenium import webdriver
from bs4 import BeautifulSoup
from writeToCSV import writeheader
import NYExtractData
from Name import Name
from datetime import datetime
from string import ascii_lowercase


def checkIfWeHaveRow(hash_from_birthdays_to_used_names, htmlRow, browser):

    # currently still html
    cells = htmlRow.findAll("td")
    parsedData = []
    # splits html row into individual elements in a list
    for cell in cells:
        parsedData += cell.contents
    rawName = parsedData[3]
    last = rawName.split(',')[0]
    firsts = rawName.split(',')[1].strip()
    fname = firsts.split(" ")[0].strip()
    try:
        mname = firsts.split(" ")[1].strip()
    except(IndexError):
        mname = ""
    lname = last.strip()
    name = Name(fname, mname, lname)

    dob = parsedData[5]
    dob = dob.split("/")
    dob = datetime(int(dob[2]), int(dob[0]), int(dob[1]))

    print(name)
    print(dob)
    try:
        print(name in hash_from_birthdays_to_used_names[dob])
        return (name in hash_from_birthdays_to_used_names[dob])
    except(KeyError):
        return False


browser = webdriver.Chrome("C:\chromedriver_win32\chromedriver.exe")
writeheader()

hash_from_birthdays_to_used_names = {}

# opening up browser
url = "http://nysdoccslookup.doccs.ny.gov/"


# maybe look into a more stripped down, efficient driver?
browser.set_page_load_timeout(10)
browser.get(url)
# time.sleep(5)

# searching for inmate last names with A
browser.find_element_by_name("M00_LAST_NAMEI").send_keys("a")
browser.find_element_by_xpath('//*[@id="il"]/form/div/div[8]/input[1]').click()  # submit button XPATH

inmatesRemaining = True

while(inmatesRemaining):
    source = browser.page_source
    # begin parsing html with beautiful soup
    soup = BeautifulSoup(source, 'html.parser')
    listOfTables = soup.findAll("table")
    inmateTable = listOfTables[0]  # each inmate table only gives us 4 results at most

    # The output in red at the bottom of the page
    errText = soup.find("p", {"class": "err"}).get_text()

    # where data is
    body = inmateTable.find("tbody")

    # find all rows with inmates
    listOfInmates = body.findAll("tr")  # verify row has a record!!!!

    # skip first dummy row
    for x in range(1, len(listOfInmates)):
        # time.sleep(5)
        currentRow = listOfInmates[x]
        if not checkIfWeHaveRow(hash_from_birthdays_to_used_names, currentRow, browser):
            NYExtractData.extract(browser, x, hash_from_birthdays_to_used_names)

    print("checking if done...")
    if("NO MORE NAMES ON FILE" in errText):
        print("done!")
        inmatesRemaining = False
    else:
        print("not done!")
        browser.find_element_by_name("next").click()

print("ending crawl")
browser.quit()




