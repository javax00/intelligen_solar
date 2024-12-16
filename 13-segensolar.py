from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
from time import sleep
from csv import writer
import pandas as pd
import pycountry
import requests
import gspread
from bs4 import BeautifulSoup
from dateutil.parser import parse
from fake_useragent import UserAgent
import platform
import random
import math
import pytz
import json
import pytz
import time
import json
import glob
import os

### LOGIN ###
username = 'Thijs@getalpha.nl'
password = 'mohfib-xupja1-hujFux'

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-segensolar.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-segensolar.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://portal.segensolar.nl/nav/pv/Module?SortOrder=Lo&Display=Gallery&PageSize=All', 'Module'],
		['https://portal.segensolar.nl/nav/pv/Inverters/MainUnits?SortOrder=Lo&Display=Gallery&PageSize=All', 'Inverter'],
		['https://portal.segensolar.nl/nav/pv/StorageSystems/HybridInverter?SortOrder=Lo&Display=Gallery&PageSize=All', 'Inverter'],
		['https://portal.segensolar.nl/nav/pv/StorageSystems/ChargerInverter?SortOrder=Lo&Display=Gallery&PageSize=All', 'Inverter'],
		['https://portal.segensolar.nl/nav/pv/Inverters/MicroInverterUnits?SortOrder=Lo&Display=Gallery&PageSize=All', 'Inverter'],
		['https://portal.segensolar.nl/nav/pv/StorageSystems/Li-ionBatteryPack?SortOrder=Lo&Display=Gallery&PageSize=All', 'Battery']]
		
# links = [['https://portal.segensolar.nl/nav/pv/Module?SortOrder=Lo&Display=Gallery&PageSize=All', 'Module']]

options = Options()
# options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
# options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--log-level=3')
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

err = 0
while err == 0:
	try:
		# driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
		driver = webdriver.Chrome(options=options, service = Service(executable_path="chromedriver.exe"))
		# driver = webdriver.Chrome(options=options, service = Service(executable_path="/Users/b2y/Work/chromedriver"))
		driver.implicitly_wait(20)
		err = 1
	except Exception:
		err = 0
		time.sleep(5)

s, i, b = [], [], []
s.append(fHeader)
i.append(fHeader)
b.append(fHeader)

driver.get('https://portal.segensolar.nl/Home/Login?ReturnUrl=%2FReseller%2FReseller%2FResellerHome')

time.sleep(5)

driver.find_element(By.ID, 'username').send_keys(username)
driver.find_element(By.ID, 'password').send_keys(password)
driver.find_element(By.ID, 'TOSAccepted').click()
driver.find_element(By.ID, 'RememberMe').click()

actions = ActionChains(driver)
actions.send_keys(Keys.TAB)
actions.perform()
time.sleep(1)
actions.send_keys(Keys.SPACE)
actions.perform()
time.sleep(50)

ws = driver.get_window_size()
driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')

driver.find_element(By.CLASS_NAME, 'submit-btn').click()
time.sleep(5)

for link in links:
	driver.get(link[0])
	time.sleep(5)

	cnt = 1
	items = driver.find_elements(By.CLASS_NAME, 'dd-product')
	for i in items:
		print('[SegenSolar] ['+link[1]+'] - ' + str(cnt)+'/'+str(len(items)))
		try:
			b = i.find_element(By.CLASS_NAME, 'dd-p-manufacturer').text
			price = i.find_element(By.CLASS_NAME, 'dd-price').text
			brand = b.split(price)[0].strip()
		except Exception as e:
			brand = ''

		try:
			name = i.find_element(By.CLASS_NAME, 'dd-p-desc').text
		except Exception as e:
			name = ''

		try:
			p = i.find_element(By.CLASS_NAME, 'dd-price').text.replace('€','')
			price = p.split(',')[0].replace('.',',')+'.'+p.split(',')[1]
		except Exception as e:
			price = ''

		try:
			prod_link = i.find_element(By.TAG_NAME, 'a').get_attribute('href')
		except Exception as e:
			prod_link = ''

		date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
		supplier = 'Segen Solar'

		stock, available, quantity = '0', '0', '0'
		stk = i.find_element(By.CLASS_NAME, 'dd-stockLevel-holder')
		if 'dd-p-instock' in stk.get_attribute('innerHTML'):
			quantity = stk.find_element(By.CLASS_NAME, 'dd-p-instock').text.split(' ')[0]
			stock = 'Yes'
		# elif 'dd-p-StockDue' in stk.get_attribute('innerHTML'):
		# 	try:
		# 		dt = stk.find_elements(By.CLASS_NAME, 'dd-p-StockDue')[0].text.split(': ')[1]
		# 	except Exception as e:
		# 		dt = stk.find_elements(By.CLASS_NAME, 'dd-p-StockDue')[0].text.split('(Bolton) ')[1]
		# 	toDt = datetime.strptime(dt, '%d %b %Y').date()
		# 	available = time.mktime(toDt.timetuple())
		elif 'dd-p-NoStock' in stk.get_attribute('innerHTML'):
			stock = '0'
		else:
			print('ERROR: '+stk.text)

		panel_size = ''
		if link[1] == 'Module':
			##### NEW TAB
			driver.execute_script("window.open('');")
			driver.switch_to.window(driver.window_handles[1])
			driver.get(prod_link)
			driver.implicitly_wait(10)
			time.sleep(3)

			c = 2
			l, w, d = '', '', ''
			try:
				ms = driver.find_elements(By.TAG_NAME, 'dl')[1].find_elements(By.TAG_NAME, 'dt')
				for m in ms:
					if 'Lengte' in m.text:
						l = driver.find_elements(By.TAG_NAME, 'dd')[c].text.replace(' mm','')
					elif 'Breedte' in m.text:
						w = driver.find_elements(By.TAG_NAME, 'dd')[c].text.replace(' mm','')
					elif 'Diepte' in m.text:
						d = driver.find_elements(By.TAG_NAME, 'dd')[c].text
					c+=1
				panel_size = l+' x '+w+' x '+d
			except Exception as e:
				panel_size = ''

			driver.close()
			driver.switch_to.window(driver.window_handles[0])
			##### NEW TAB

		append_list_as_row(filepathHeaderCSV, [brand, name, link[1], panel_size, 'Netherlands', stock, available, quantity, date, supplier, prod_link, price, quantity])
		cnt+=1

driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'SEGENSOLAR'
num = '16'

if platform.system() == 'Windows':
	loc = 'G:\\Other computers\\My MacBook Air\\Intelligen\\'+filepathHeaderCSV
elif platform.system() == 'Darwin':
	loc = '/Users/b2y/Work/Intelligen/'+filepathHeaderCSV

options = Options()
# options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
# options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

err = 0
while err == 0:
	try:
		# driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
		driver = webdriver.Chrome(options=options, service = Service(executable_path="chromedriver.exe"))
		driver.implicitly_wait(10)
		driver.minimize_window()
		# driver.get('https://xsolarx.com')
		driver.get('https://xsolarx.com/user')
		err = 1
	except Exception:
		err = 0
		time.sleep(5)
time.sleep(2)

driver.find_element(By.ID, 'edit-name').send_keys('glennkarlnavarra008@gmail.com')
driver.find_element(By.ID, 'edit-pass').send_keys('Navarra12321!')
driver.find_element(By.CLASS_NAME, 'form-submit').click()
time.sleep(2)

agin = 0
while agin == 0:
	driver.get('https://xsolarx.com/feed/'+num+'/edit')
	time.sleep(2)

	# UNLOCK AND SAVE
	body = driver.find_element(By.TAG_NAME, 'body').text
	if 'Unlock and Save' in body:
		driver.find_elements(By.CLASS_NAME, 'form-submit')[1].click()
		time.sleep(2)
		driver.get('https://xsolarx.com/feed/'+num+'/edit')
		time.sleep(2)

	WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'edit-plugin-fetcher-source-remove-button'))).click()
	time.sleep(2)

	driver.find_element(By.CLASS_NAME, 'form-file').send_keys(loc)
	time.sleep(5)
	driver.find_element(By.CLASS_NAME, 'text-full').click()
	time.sleep(2)
	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.TAB)
	time.sleep(3)

	driver.find_elements(By.CLASS_NAME, 'form-submit')[1].click()

	c = 1
	done = 0
	while done == 0:
		try:
			body = driver.find_element(By.TAG_NAME, 'body').text
			if 'has been updated' in body or '1 second ago' in body:
				done = 1
				agin = 1
				print('UPLOADING '+str(name)+' - DONE\n')
			elif 'Fetching:' in body:
				print('UPLOADING '+str(name)+' - '+str(c*5)+'secs - upload...')
				done = 0
				agin = 1
			elif 'Error message' in body:
				done = 0
				agin = 1
				print('Reloading...')
				driver.refresh()
				time.sleep(5)
				c = 1
			else:
				done = 1
				agin = 0
				print(body)
				print('['+str(link.index(x)+1)+'/'+str(len(link))+'] '+'ERROR: Try again.')
			time.sleep(5)
			c+=1
		except Exception as e:
			done = 0
			pass
driver.quit()
print('ALL DONE!')