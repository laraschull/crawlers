from selenium import webdriver
from bs4 import BeautifulSoup
import time
import ExtractData

url = "http://www.ctinmateinfo.state.ct.us/searchop.asp"
browser = webdriver.Chrome()
browser.set_page_load_timeout(10)
browser.get(url)
time.sleep(5)
browser.find_element_by_name("nm_inmt_last").send_keys("A")
browser.find_element_by_name("submit1").click()
source = browser.page_source
soup = BeautifulSoup(source, 'html.parser')
listOfTables = soup.findAll("table")
inmateTable = listOfTables[1]
body = inmateTable.find("tbody")
listOfInmates = body.findAll("tr")
for x in range(1, 6):

    time.sleep(5)
    currentRow = listOfInmates[x]
    ExtractData.inmateRowToList(currentRow)
# print(soup.body)
# with open('test.txt', 'w') as file:
#     file.write(str(soup))
time.sleep(10)
browser.quit()