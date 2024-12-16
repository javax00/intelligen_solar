from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
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
username = 'thijs@getalpha.nl'
password = 'Gw&7Wm&5Wb&4Da#'


def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-keno.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-keno.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)


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
		# driver.minimize_window()
		ws = driver.get_window_size()
		driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')
		err = 1
	except Exception as e:
		print(str(e))
		err = 0
		time.sleep(5)

s, i, a, b = [], [], [], []
s.append(fHeader)
i.append(fHeader)
a.append(fHeader)
b.append(fHeader)

driver.get('https://b2b.keno-energy.com/login')
time.sleep(5)

driver.find_element(By.ID, "login-form-email").send_keys(username)
driver.find_element(By.ID, "login-form-password").send_keys(password)
driver.find_element(By.ID, "login-form-submit").click()
time.sleep(20)

driver.find_element(By.ID, 'lang-change-dropdown').click()
time.sleep(1)
driver.find_elements(By.ID, 'lang')[6].click()
time.sleep(5)

links = [[0, 'Module'],
		[1, 'Inverter'],
		[4, 'Battery']]

for link in links:
	driver.find_elements(By.CLASS_NAME, 'main-menu-option')[link[0]].click()
	time.sleep(5)

	scroll = 0
	count = 1
	while scroll == 0:
		if 'product-card-lazyload' in driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML'):
			scroll = 0
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(1)
			print('Scrolling '+str(count)+'...')
			count+=1
		else:
			scroll = 1
			print('Done scrolling...')

	prods = driver.find_elements(By.CLASS_NAME, 'product-card__quick')

	count = 1
	for prod in prods:
		title = prod.find_element(By.CLASS_NAME, 'product-card--name-heading').text.split(' - ')
		brand = title[0]
		name = title[1]
		avail = 0
		price = 0
		supplier = 'KENO'
		date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')

		if 'availability-table' in prod.get_attribute('innerHTML'):
			if 'data-quantity' in prod.get_attribute('innerHTML'):
				quan = prod.find_element(By.CLASS_NAME, 'availability-table').get_attribute('data-quantity')
			else:
				quan = prod.find_elements(By.TAG_NAME, 'nobr')[1].find_elements(By.TAG_NAME, 'span')[-1].text.strip().split(' ')[0]
		else:
			quan = 0

		if quan == 0:
			stock = 0
		else:
			stock = 'Yes'

		if 'product-card--price' in prod.get_attribute('innerHTML'):
			get_price = prod.find_elements(By.CLASS_NAME, 'align-items-end')

			if len(get_price) == 2:
				price = get_price[-1].text.strip().split(' ')[0]
			elif len(get_price) == 1:
				price = get_price[0].find_element(By.TAG_NAME, 'div').text.strip().split(' ')[0]

		print('[Keno] ['+link[1]+'] - '+str(count)+'/'+str(len(prods)))

		append_list_as_row(filepathHeaderCSV, [brand, name, link[1], '0', 'UK', stock, avail, quan, date, supplier, '', price, quan])

		count+=1

driver.quit()
##################################################################################################################
print('UPLOADING NOW...')

name = 'Keno'
num = '20'

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