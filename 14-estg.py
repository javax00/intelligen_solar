from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timezone
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
username = 'thijs@getalpha.nl'
password = 'puxWug-pyqte9-bovsox'

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-estg.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-estg.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://www.estg.eu/en-gb/solar-panels/', 'Module'],
		['https://www.estg.eu/en-gb/inverters/', 'Inverter'],
		['https://www.estg.eu/en-gb/mounting-materials/', 'Accessory'],
		['https://www.estg.eu/en-gb/solar-battery-storage/', 'Battery']]

# links = [['https://www.estg.eu/en-gb/solar-panels/', 'Module']]

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
		driver.implicitly_wait(20)
		ws = driver.get_window_size()
		driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')
		err = 1
	except Exception:
		err = 0
		time.sleep(5)

driver.get('https://www.estg.eu/en-gb/customer/account/login')
time.sleep(5)

try:
	driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll').click()
except Exception as e:
	pass

# try:
# 	driver.find_element(By.CLASS_NAME, 'c-button').click()
# 	time.sleep(2)
# except Exception as e:
# 	pass

# LOGIN ONLY
driver.find_element(By.ID, 'email').send_keys(username)
driver.find_element(By.ID, 'password').send_keys(password)
driver.find_elements(By.ID, 'send2')[1].click()
time.sleep(5)

for link in links:
	nxtPg = 0
	cnt = 1
	driver.get(link[0])
	time.sleep(5)

	price = 0
	stock = 0
	available = 0

	while nxtPg == 0:
		prods = driver.find_elements(By.CLASS_NAME, 'card__product')
		for prod in prods:
			tot = driver.find_elements(By.CLASS_NAME, 'toolbar-amount')[0].text.split(' ')
			if 'Items' in tot[-1]:
				print('[ESTG] ['+link[1]+'] - ' + str(cnt)+'/'+tot[0])
			else:
				print('[ESTG] ['+link[1]+'] - ' + str(cnt)+'/'+tot[-1])

			try:
				if 'card__manufacturer' in prod.get_attribute('innerHTML'):
					brand = prod.find_element(By.CLASS_NAME, 'card__manufacturer').text.strip()
				else:
					brand = ''
			except Exception:
				pass

			try:
				name = prod.find_element(By.CLASS_NAME, 'card__title').text.strip()
			except Exception:
				pass


			try:
				prod_link = prod.find_element(By.CLASS_NAME, 'card__image').get_attribute('href')
			except Exception:
				pass

			# LOGIN ONLY
			try:
				if 'price-from' in prod.get_attribute('innerHTML'):
					price = prod.find_element(By.CLASS_NAME, 'price-box').text.strip().split('€')[1]
				if 'special-price' in prod.get_attribute('innerHTML'):
					price = prod.find_element(By.CLASS_NAME, 'special-price').text.strip().replace('€','')
			except Exception:
				pass

			panel_size = '0'
			if link[1] == 'Module':
				##### NEW TAB
				driver.execute_script("window.open('');")
				driver.switch_to.window(driver.window_handles[1])
				driver.get(prod_link)
				driver.implicitly_wait(10)
				time.sleep(3)

				driver.find_elements(By.CLASS_NAME, 'read-more-trigger')[-1].click()
				time.sleep(1)
				tr = driver.find_elements(By.ID, 'product-attribute-specs-table')[1].find_elements(By.TAG_NAME, 'tr')
				dim = ''
				for r in tr:
					if 'Length (mm)' in r.text:
						dim += r.find_element(By.TAG_NAME, 'td').text
					elif 'Width (mm)' in r.text:
						dim += ' x '
						dim += r.find_element(By.TAG_NAME, 'td').text
					elif 'Height (mm)' in r.text:
						dim += ' x '
						dim += r.find_element(By.TAG_NAME, 'td').text
				panel_size = dim

				driver.close()
				driver.switch_to.window(driver.window_handles[0])
				##### NEW TAB

			# LOGIN ONLY
			try:
				stock_info = prod.find_element(By.CLASS_NAME, 'availability-status').text
			except Exception:
				pass

			if 'on stock' in stock_info:
				stock = 'Yes'
				available = '0'
				quantity = stock_info.split(' items')[0]
			# elif 'week' in stock_info:
			# 	stock = '0'
			# 	available = '0'
			# 	quantity = '0'
			# elif 'Expected' in stock_info:
			# 	stock = '0'
			# 	full_month_date = stock_info.replace('Expected on ','')
			# 	full_month_format = "%b %d, %Y"
			# 	d = datetime.strptime(full_month_date, full_month_format)
			# 	available = str(int(d.replace(tzinfo=timezone.utc).timestamp()))
			else:
				stock = '0'
				available = '0'
				quantity = '0'

			date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
			supplier = 'ESTG'

			append_list_as_row(filepathHeaderCSV, [brand, name, link[1], panel_size, 'Netherlands', stock, available, quantity, date, supplier, prod_link, price, quantity])
			cnt += 1

		if 'item pages-item-next' in driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML'):
			driver.execute_script("arguments[0].scrollIntoView();", prods[-1])
			time.sleep(5)
			driver.find_element(By.CLASS_NAME, 'toolbar__footer').find_element(By.CLASS_NAME, 'next').click()
			time.sleep(5)
			nxtPg = 0
		else:
			nxtPg = 1

driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'ESTG'
num = '17'

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






