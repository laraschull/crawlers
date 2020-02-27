from selenium import webdriver
from bs4 import BeautifulSoup
import time
import ExtractData

#opening up browser
url = "http://www.ctinmateinfo.state.ct.us/searchop.asp"
browser = webdriver.Chrome()  # maybe look into a more stripped down, efficient driver?
browser.set_page_load_timeout(10)
browser.get(url)
time.sleep(5)

#searching for inmate last names with A
browser.find_element_by_name("nm_inmt_last").send_keys("A")
browser.find_element_by_name("submit1").click()
source = browser.page_source

#begin parsing html with beautiful soup
soup = BeautifulSoup(source, 'html.parser')
listOfTables = soup.findAll("table")

#need to start at 1 because first table is headers
inmateTable = listOfTables[1]

#where data is
body = inmateTable.find("tbody")

#find all rows with inmates
listOfInmates = body.findAll("tr")

#taking rows 2-7
#first row is header, so skip
for x in range(1, 6):

    #allows time to go through db to avoid getting IP banned due to suspcious activity
    time.sleep(5)
    currentRow = listOfInmates[x]
    ExtractData.inmateRowToList(currentRow)
# print(soup.body)
# with open('test.txt', 'w') as file:
#     file.write(str(soup))
time.sleep(10)
browser.quit()