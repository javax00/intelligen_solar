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
password = 'megbec-zybva1-zYvqyw'

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-hadec.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-hadec.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://hadec.nl/shop/zonnepanelen.html', 'Module'],
		['https://hadec.nl/shop/omvormers.html', 'Inverter'],
		['https://hadec.nl/shop/energie-opslag.html', 'Battery']]

# links = [['https://hadec.nl/shop/energie-opslag.html', 'Battery']]

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

options.add_argument("--disable-logging")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-browser-side-navigation")
options.add_argument("--ignore-ssl-errors")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--force-device-scale-factor=1")
options.add_argument("--aggressive-cache-discard")
options.add_argument("--disable-cache")
options.add_argument("--disable-application-cache")
options.add_argument("--disable-offline-load-stale-cache")
options.add_argument("--disk-cache-size=0")

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

s, i, b = [], [], []
s.append(fHeader)
i.append(fHeader)
b.append(fHeader)

driver.get('https://hadec.nl/customer/account/login/referer/aHR0cHM6Ly9oYWRlYy5ubC9zaG9wL3pvbm5lcGFuZWxlbi5odG1s/')
time.sleep(10)

driver.find_element(By.ID, 'email').send_keys(username)
driver.find_elements(By.ID, 'pass')[0].send_keys(password)
time.sleep(2)
driver.find_element(By.ID, 'send2').click()
time.sleep(10)

if 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll' in driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML'):
	driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
	time.sleep(2)

for link in links:
	driver.get(link[0])
	time.sleep(5)

	if 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll' in driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML'):
		driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
		time.sleep(2)

	c = 0
	cnt = 1
	while c == 0:
		print('~'+link[1]+'] Page: '+str(cnt))
		items = driver.find_elements(By.CLASS_NAME, 'product__item')
		for i in items:

			brand=name=price=stk=''

			if 'product__additional' in i.get_attribute('innerHTML'):
				brand = i.find_element(By.CLASS_NAME, 'product__additional').text

			if 'product__name' in i.get_attribute('innerHTML'):
				name = i.find_element(By.CLASS_NAME, 'product__name').text

			if 'data-price-amount' in i.get_attribute('innerHTML'):
				try:
					price = i.find_element(By.CLASS_NAME, 'product__bottom-hover').find_elements(By.CLASS_NAME, 'price-wrapper')[0].get_attribute('data-price-amount')
				except Exception:
					price = ''

			if 'product__image-container' in i.get_attribute('innerHTML'):
				prod_link = i.find_element(By.CLASS_NAME, 'product__image-container').get_attribute('href')

			date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
			supplier = 'Hadec'

			if 'product__stock-indicator' in i.get_attribute('innerHTML'):
				stk = i.find_element(By.CLASS_NAME, 'product__stock-indicator').text

			if 'Informeer naar levertijd' in stk or stk == '':
				stock = '0'
				quantity = '0'
			elif 'Op voorraad' in stk:
				stock = 'Yes'

				##### NEW TAB
				driver.execute_script("window.open('');")
				driver.switch_to.window(driver.window_handles[1])
				driver.get(prod_link)

				time.sleep(1)
				if 'product__stock-indicator' in driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML'):
					quantity = driver.find_element(By.CLASS_NAME, 'product__stock-indicator').text.split(' ')[0]

				driver.close()
				driver.switch_to.window(driver.window_handles[0])
				##### NEW TAB

			append_list_as_row(filepathHeaderCSV, [brand, name, link[1], '0', 'Netherlands', stock, '0', quantity, date, supplier, prod_link, price, quantity])

		try:
			nxt = driver.find_element(By.CLASS_NAME, 'product__list-bottom-container')
			if 'next' in nxt.get_attribute('innerHTML'):
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(1)
				# nxt.find_element(By.CLASS_NAME, 'next').click()

				element = nxt.find_element(By.CLASS_NAME, 'next')
				driver.execute_script("arguments[0].click();", element)

				time.sleep(10)
				cnt+=1
				c = 0
			else:
				if cnt == 1:
					driver.refresh()
					time.sleep(2)
					driver.refresh()
					time.sleep(2)
					c = 0
				else:
					c = 1
		except Exception as e:
			c = 1
driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'HADEC'
num = '13'

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