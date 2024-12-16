from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd
import gspread
import time
import glob
import os

options = Options()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
chrome_prefs = {"download.default_directory": r"/Users/b2y/Downloads"}
options.experimental_options["prefs"] = chrome_prefs

driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
driver.get("https://seller.walmart.com/partner-analytics/overview?program=ALL&duration=WMT_FISCAL_YTD")
driver.implicitly_wait(5)

print('logging in...')
driver.find_elements(By.CLASS_NAME, "form-control__formControl___3uDUX")[0].send_keys('glennkarlnavarra008@gmail.com')
time.sleep(2)
driver.find_elements(By.CLASS_NAME, "form-control__formControl___3uDUX")[1].send_keys('Navarra123!')
time.sleep(2)
driver.find_element(By.CLASS_NAME, "app-btn").click()
time.sleep(8)

ad = 0
while ad == 0:
	try:
		driver.find_element(By.CLASS_NAME, "_pendo-close-guide").click()
		print('ad closing...')
		time.sleep(5)
		ad = 0
	except Exception as e:
		ad = 1
		print('ad done...')
		time.sleep(3)

driver.find_element(By.CLASS_NAME, "Popover-module_popoverContainer__2JyDf").click()
time.sleep(1)
driver.find_element(By.CLASS_NAME, "Options-module_bodyContainer__bQYPN").find_elements(By.TAG_NAME, "tr")[7].click()
time.sleep(3)

driver.find_element(By.CLASS_NAME, "pl-8").click()
print('downloading...')
time.sleep(5)

print('retrieving and uploading file...')
list_of_files = glob.glob('/Users/b2y/Downloads/*')
latest_file = max(list_of_files, key=os.path.getctime)

df = pd.read_csv(latest_file, low_memory=False)

final = []
for i in df.index:
	temp = []
	for x in df:
		if x == 'Date':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'GMV':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'GMV % Change':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'GMV - Commission':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Units Sold':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Orders':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'AUR':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
	final.append(temp)
driver.close()
os.remove(latest_file)

# gc = gspread.service_account(filename='/Users/b2y/Work/Intelligen/credentials/walmart-report-fabb9d82501c.json')
# sh = gc.open("Autumn Star - Walmart")
# ws = sh.worksheet('Overview-Data')

gc = gspread.service_account(filename='/Users/b2y/Work/Intelligen/credentials/walmart-report-fabb9d82501c.json')
sh = gc.open("Dropshipping Dashboard - Amazon/Walmart")
ws = sh.worksheet('DataOverview-WMRT')

col = len(ws.col_values(1))
# ws.delete_rows(2,len(col))
sh.values_clear("DataOverview-WMRT!A2:G"+str(col))

col = ws.col_values(1)
ws.update('A2', final)

print('done.')













