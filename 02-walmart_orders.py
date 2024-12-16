from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd
import warnings
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
driver.get("https://seller.walmart.com/order-management/details")
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

print('click New Orders')
driver.find_elements(By.CLASS_NAME, "Card-module_card__zeE7r")[2].find_element(By.TAG_NAME, 'a').click()
time.sleep(5)

print('downloading...')
driver.find_element(By.CLASS_NAME, "_1ikNO").click()
time.sleep(1)
driver.find_element(By.CLASS_NAME, "_1LdPv").find_elements(By.TAG_NAME, 'li')[2].click()
time.sleep(10)

print('retrieving and uploading file...')
list_of_files = glob.glob('/Users/b2y/Downloads/*')
latest_file = max(list_of_files, key=os.path.getctime)

warnings.simplefilter("ignore")
df = pd.read_excel(latest_file, engine="openpyxl")

final = []
for i in df.index:
	temp = []
	for x in df:
		if x == 'PO#':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Order#':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Order Date':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Ship By':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Delivery Date':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Customer Name':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Customer Shipping Address':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Customer Phone Number':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Ship to Address 1':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Ship to Address 2':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'City':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'State':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Zip':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Segment':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'FLIDS':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Line#':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'UPC':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Status':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Item Description':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Shipping Method':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Shipping Tier':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Shipping SLA':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Shipping Config SOurce':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Qty':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'SKU':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Item Cost':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Shipping Cost':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Tax':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Update Status':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Update Qty':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Carrier':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Tracking Number':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Tracking Url':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Seller Order NO':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Fulfillment Entity':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Replacement Order':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Original Customer Order Id':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Customer Intent To Cancel':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
		elif x == 'Intent To Cancel Override':
			if str(df[x][i]) == 'nan':
				temp.append('')
			else:
				temp.append(str(df[x][i]))
	final.append(temp)
driver.close()
os.remove(latest_file)

gc = gspread.service_account(filename='/Users/b2y/Work/Intelligen/credentials/walmart-report-fabb9d82501c.json')
sh = gc.open("Wamart Order Downloads 2022 (Monthly)")
ws = sh.worksheet('New Orders')

col = len(ws.col_values(1))
# ws.delete_rows(2,len(col))
sh.values_clear("New Orders!A2:AM"+str(col))

col = ws.col_values(1)
ws.update('A2', final)

print('done.')













