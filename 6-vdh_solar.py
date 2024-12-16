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
username = 'Thijs@getalpha.nl'
password = 'rakper-1cypMu-nynqaq'

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-vdh-solar.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-vdh-solar.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

brands = ['solaredge',
		'aeg',
		'dmegc',
		'rec',
		'enphase',
		'apsystems',
		'aps',
		'goodwe',
		'huawei',
		'lg',
		'solaredge_ev']

# links = [['https://www.vdh-solar.nl/c-solar-panels', 'Module'],
# 		['https://www.vdh-solar.nl/c-inverters', 'Inverter']]


links = [['https://www.vdh-solar.nl/c-zonnepanelen', 'Module'],
		['https://www.vdh-solar.nl/c-omvormers', 'Inverter']]

# links = [['https://www.vdh-solar.nl/c-solar-panels', 'Module']]

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

# driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
driver = webdriver.Chrome(options=options, service = Service(executable_path="chromedriver.exe"))
driver.implicitly_wait(10)
# driver.minimize_window()
ws = driver.get_window_size()
driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')

s, i = [], []
s.append(fHeader)
i.append(fHeader)

driver.get('https://www.vdh-solar.nl/login')
time.sleep(random.randint(3, 5))

try:
	driver.find_elements(By.ID, 'eu-cookie-ok')[0].click()
	time.sleep(random.randint(3, 5))
except Exception as e:
	pass

driver.find_element(By.CLASS_NAME, 'email').send_keys(username)
time.sleep(random.randint(3, 5))
driver.find_element(By.CLASS_NAME, 'password').send_keys(password)
time.sleep(random.randint(3, 5))
driver.find_element(By.CLASS_NAME, 'login-button').click()
time.sleep(random.randint(3, 5))


for link in links:
	driver.get(link[0])

	try:
		driver.find_element(By.CLASS_NAME, 'ok-button').click()
		time.sleep(1)
		driver.find_element(By.CLASS_NAME, 'language-list').click()
		driver.find_element(By.CLASS_NAME, 'language-list').find_elements(By.TAG_NAME, 'li')[1].find_element(By.TAG_NAME, 'a').click()
	except Exception:
		pass

	print('scrolling...')
	scroll = 0
	while scroll == 0:
		try:
			time.sleep(random.randint(2, 3))
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			display = driver.find_element(By.CLASS_NAME, 'infinite-scroll-loader').get_attribute('style')
			if str(display) == 'display: block;':
				scroll = 0
			else:
				scroll = 1
		except Exception:
			scroll = 0

	print('done scrolling...')

	prods = []
	temp = driver.find_elements(By.CLASS_NAME, 'product-item')
	for y in temp:
		prods.append(y.find_elements(By.TAG_NAME, 'a')[1].get_attribute('href'))

	for prod in prods:
		print('[VDH] ['+link[1]+'] - '+str(prods.index(prod)+1)+'/'+str(len(prods)))
		driver.get(prod)
		time.sleep(random.randint(1, 3))

		try:
			price = driver.find_element(By.CLASS_NAME, 'product-price    ').text.replace(',','.').replace('€','').strip()
		except Exception as e:
			price = driver.find_element(By.CLASS_NAME, 'prices-table').find_elements(By.CLASS_NAME, 'item-price')[0].text.replace(',','.').replace('€','').strip()

		brand, name, panel_size = '0', '0', '0'
		date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
		try:
			tab = driver.find_elements(By.CLASS_NAME, 'ui-tabs-tab')[1].text
		except Exception:
			tab = ''

		if tab != 'SPECIFICATIES':
			name = driver.find_element(By.TAG_NAME, 'h1').text.strip()
			if name.split(' ')[0].lower() in brands:
				brand = name.split(' ')[0]
				name = name[name.index(' ')+1:]
		else:
			name = driver.find_element(By.TAG_NAME, 'h1').text.strip().replace(brand+' ', '')

			try:
				agn = 0
				specs = ''
				while agn == 0:
					driver.find_elements(By.CLASS_NAME, 'ui-tabs-tab')[1].click()
					time.sleep(random.randint(1.5, 3))
					temp1 = driver.find_elements(By.CLASS_NAME, 'data-table')[0]
					specs = temp1.find_elements(By.TAG_NAME, 'tr')
					if temp1.text == '':
						agn = 0
					else:
						agn = 1

				for spec in specs:
					if spec.find_element(By.CLASS_NAME, 'spec-name').text.strip() == 'Merk':
						brand = spec.find_element(By.CLASS_NAME, 'spec-value').text.strip()

					if link[1] == 'Module':
						if spec.find_element(By.CLASS_NAME, 'spec-name').text.strip() == 'Afmeting':
							panel_size = spec.find_element(By.CLASS_NAME, 'spec-value').text.strip()
			except Exception as e:
				pass
		append_list_as_row(filepathHeaderCSV, [brand, name, link[1], panel_size, 'Netherlands', 'Yes', 0, 0, date, 'VDH Solar', prod, price, 0])

driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'VDH_SOLAR'
num = '8'

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