from selenium import webdriver
from bs4 import BeautifulSoup
from writeToCSV import writeheader
import ExtractData
from string import ascii_lowercase

browser = webdriver.Chrome()
writeheader()

for s in ascii_lowercase:

    # opening up browser
    url = "http://www.ctinmateinfo.state.ct.us/searchop.asp"
    # maybe look into a more stripped down, efficient driver?
    browser.set_page_load_timeout(10)
    browser.get(url)
    # time.sleep(5)

    # searching for inmate last names with A
    browser.find_element_by_name("nm_inmt_last").send_keys(s)
    browser.find_element_by_name("submit1").click()
    source = browser.page_source

    # begin parsing html with beautiful soup
    soup = BeautifulSoup(source, 'html.parser')
    listOfTables = soup.findAll("table")

    # need to start at 1 because first table is headers
    inmateTable = listOfTables[1]

    # where data is
    body = inmateTable.find("tbody")

    # find all rows with inmates
    listOfInmates = body.findAll("tr")

    # skip first dummy row

    for x in range(1, len(listOfInmates)-1):

        # time.sleep(5)
        currentRow = listOfInmates[x]
        ExtractData.inmateRowToList(currentRow, browser)

browser.quit()
