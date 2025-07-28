from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
import Variable_Config as v

from_date = v.START_DATE
to_date = v.END_DATE

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-features=UseXNNPACK")
# prefs = {
#     #"profile.default_content_settings.popups": 0,
#     "download.default_directory": v.OUTPUT_FILE_LOCATION, 
#     #"download.prompt_for_download": False,
#     "download.directory_upgrade": True
# }
# chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)

driver.get(r"https://www.iexindia.com/")
wait = WebDriverWait(driver, 600)
 
# three bars on top right
ele = wait.until(EC.presence_of_element_located((
    By.XPATH, "/html/body/div[1]/div[2]/nav[1]/button")))
ele.click()

if v.EVALUATION: print("Three bars clicked")

# click on market data section
ele=wait.until(EC.presence_of_element_located((
    By.XPATH, "/html/body/div[2]/div[3]/div/ul/div[2]/div[1]")))
ele.click()

if v.EVALUATION: print("Market Data clicked")

if v.SEGMENT=='DAM':
    # click on DAM 
    ele = wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[2]/div[3]/div/ul/div[2]/div[2]/div/div/div/a[1]/div")))
    ele.click()
elif v.SEGMENT=='GDAM':
    # click on GDAM
    ele = wait.until(EC.presence_of_element_located((
        By.LINK_TEXT, "Green Day Ahead Market")))
    ele.click()
elif v.SEGMENT=='HPDAM':
    # click on HPDAM
    ele = wait.until(EC.presence_of_element_located((
        By.LINK_TEXT, "High Price Day Ahead Market")))
    ele.click()
elif v.SEGMENT=='RTM':
    # click on RTM
    ele = wait.until(EC.presence_of_element_located((
        By.LINK_TEXT, "Real Time Market")))
    ele.click()
elif v.SEGMENT=='TAM':
    # click on TAM
    ele = wait.until(EC.presence_of_element_located((
        By.LINK_TEXT, "Intra Day, Day Ahead Contingency (DAC), Term Ahead Market")))
    ele.click()
elif v.SEGMENT=='GTAM':
    # click on GTAM
    ele = wait.until(EC.presence_of_element_located((
        By.LINK_TEXT, "Green Intra Day, Day Ahead Contingency (DAC), Term Ahead Market")))
    ele.click()
else: exit("Cannot Download Report Unhandled Segment")

if v.EVALUATION: print("Segment clicked")

if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM']:
    # click on range selection button
    ele= wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[2]/div[1]/div[2]/div/div/div/div")))
    ele.click()

    if v.EVALUATION: print("Range Selection clicked")

elif v.SEGMENT in ['TAM']:
    # click on trade period selection button
    ele= wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[2]/div[3]/div/div/div/div/div/div")))
    ele.click()

    if v.EVALUATION: print("Trade Period clicked")

elif v.SEGMENT in ['GTAM']:
    # click on trade period selection button
    ele=wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[3]/div/div/div/div/div/div")))
    ele.click()
    
    if v.EVALUATION: print("Trade Period clicked")
else: exit("Unhandled Segment when trying to download report")

# click on -select range- option
ele= wait.until(EC.presence_of_element_located((
    By.XPATH, "/html/body/div[3]/div[3]/ul/li[6]")))
ele.click()

if v.EVALUATION: print("-select range- clicked")

# click on from date option
if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM']:
    ele= wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[2]/div[1]/div[3]/div/div/input")))
    ele.click()
elif v.SEGMENT in ['TAM']:
    ele= wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[2]/div[3]/div[2]/div/div/input")))#"//input[@placeholder,'DD-MM-YYYY']")))
    ele.click()
elif v.SEGMENT in ['GTAM']:
    ele= wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[3]/div[2]/div/div/input")))
    ele.click()


if v.EVALUATION: print("from date clicked")

# send keys dd mm yyyy
ele.send_keys(''.join(from_date.split('-')))

if v.EVALUATION: print("from date inputted")

# click on to date option
if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM']:
    ele= wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[2]/div[1]/div[4]/div/div/input")))
    ele.click()
elif v.SEGMENT in ['TAM']:
    ele= wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[2]/div[3]/div[3]/div/div/input")))
        #By.CLASS_NAME, "MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedEnd mui-w1jawv")))
    ele.click()
elif v.SEGMENT in ['GTAM']:
    ele= wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[3]/div[3]/div/div/input")))
    ele.click()

else: exit("Unhandled Segment")

if v.EVALUATION: print("to date clicked")

# send keys dd mm yyyy 
ele.send_keys(''.join(to_date.split('-')))

if v.EVALUATION: print("to date inputted")

# click on update report button
if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM','TAM','GTAM']:
    ele= wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[1]/div[2]/button")))
    ele.click()
elif v.SEGMENT in ['GDAM']:
    ele=wait.until(EC.presence_of_element_located((
        By.NAME, "Update Report")))
 
    #wait.until(EC.presence_of_element_located(( By.XPATH, "//button[span[text()='Update Report']]")))

    #wait.until(EC.text_to_be_present_in_element((By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[1]/div[2]/button"), "Update Report"))
    #wait.until(EC.presence_of_element_located((
        #By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[1]/div[2]/button/span")))
    ele.click()
    

if v.EVALUATION: print("update report clicked")

# wait for some time till report is updated
if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM']:
    wait.until(EC.text_to_be_present_in_element((By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[3]/div[1]/table/tbody/tr[1]/td[1]"), from_date[2:]))
    if v.EVALUATION: print("waited for report to update")
elif v.SEGMENT in ['TAM','GTAM']:
    wait.until(EC.text_to_be_present_in_element((By.XPATH, "/html/body/div[1]/div[4]/section/div[2]/div[1]/table/tbody/tr[1]/td[1]"),from_date[2:]))

# click on export button
ele= wait.until(EC.presence_of_element_located((
    By.XPATH, "/html/body/div[1]/div[4]/section/div[1]/div[1]/div[2]/div/button")))
ele.click()

if v.EVALUATION: print("export button clicked")

# click on Export Excel
ele= wait.until(EC.presence_of_element_located((
    By.XPATH, "/html/body/div[3]/div[3]/div/button[1]")))
ele.click()

if v.EVALUATION: print("export excel clicked")

time.sleep(3)

# waits for all the files to be completed and returns the paths
import os
import glob

def downloads_done():
    while True:
        for i in os.listdir(v.DOWNLOADS_PATH):
            if ".crdownload" in i:
                time.sleep(0.5)
                downloads_done()
        else: break

downloads_done()
if v.EVALUATION: print("DOWNLOADS DONE")
driver.close()

#home = os.path.expanduser("~")
#downloadspath=os.path.join(home, "Downloads")
list_of_files = glob.glob(v.DOWNLOADS_PATH+r"\*") # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)

if v.EVALUATION: print("INPUT FILE LOCATION: ",latest_file)
v.INPUT_FILE_LOCATION=latest_file

