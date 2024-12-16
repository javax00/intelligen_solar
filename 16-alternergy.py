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
username = 'thinqsolar@outlook.com'
password = 'kixqoR-semvep-6zawxy'

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-alternergy.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-alternergy.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://www.alternergy.co.uk/products/solar-pv-panels', 'Module'],
		['https://www.alternergy.co.uk/products/solar-inverters', 'Inverter'],
		['https://www.alternergy.co.uk/products/solar-pv-battery-storage', 'Battery']]

# links = [['https://www.alternergy.co.uk/products/solar-pv-panels', 'Module']]

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
		# driver.minimize_window()
		ws = driver.get_window_size()
		driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')
		err = 1
	except Exception:
		err = 0
		time.sleep(5)

driver.get('https://www.alternergy.co.uk/customer/account/login')
time.sleep(5)

driver.find_element(By.ID, 'email').send_keys(username)
driver.find_element(By.ID, 'pass').send_keys(password)
driver.find_elements(By.ID, 'send2')[0].click()
time.sleep(5)

for link in links:
	driver.get(link[0])

	l = 0
	while l == 0:
		print('[Alternergy] ['+link[1]+'] - Scrolling')

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(5)
		a = driver.find_element(By.CLASS_NAME, 'infinite-loader').get_attribute('style')
		if a == '':
			driver.find_element(By.CLASS_NAME, 'btn-load-more').click()
			l = 0
		else:
			l = 1
			print('[Alternergy] ['+link[1]+'] - Done Scrolling')
		time.sleep(3)

	ol = driver.find_element(By.CLASS_NAME, 'product-items')
	prod_links = []
	for li in ol.find_elements(By.TAG_NAME, 'li'):
		prod_links.append(li.find_element(By.CLASS_NAME, 'product-item-link').get_attribute('href'))

	cnt = 1
	for prod_link in prod_links:
		try:
			print('[Alternergy] ['+link[1]+'] - ' + str(cnt)+'/'+str(len(prod_links)))
			driver.get(prod_link+'#additional')
			time.sleep(2)

			tr = driver.find_element(By.ID, 'product-attribute-specs-table').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
			for t in tr:
				if t.find_element(By.TAG_NAME, 'th').text == 'Brand':
					brand = t.find_element(By.TAG_NAME, 'td').text

			name = driver.find_element(By.CLASS_NAME, 'page-title').text.replace(brand,'')

			date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
			supplier = 'ESTG'

			if link[1] == 'Module':
				l,w,z = '','',''
				for t in tr:
					if t.find_element(By.TAG_NAME, 'th').text == 'Length (mm)':
						l = t.find_element(By.TAG_NAME, 'td').text
					if t.find_element(By.TAG_NAME, 'th').text == 'Width (mm)':
						w = t.find_element(By.TAG_NAME, 'td').text
					if t.find_element(By.TAG_NAME, 'th').text == 'Thickness (mm)':
						z = t.find_element(By.TAG_NAME, 'td').text
				panel_size = l+' x '+w+' x '+z+' mm'
			else:
				panel_size = ''

			stck = driver.find_element(By.CLASS_NAME, 'stock')
			if 'in-stock-note' in stck.get_attribute('innerHTML'):
				stock = 'Yes'
				available = '0'
				quantity = stck.find_element(By.CLASS_NAME, 'in-stock-note').text.split(' ')[0]
			elif 'back-note' in stck.get_attribute('innerHTML'):
				stock = '0'
				available = stck.find_element(By.CLASS_NAME, 'back-note').text.split(' ')[2]
				quantity = '0'
			else:
				stock = '0'
				available = '0'
				quantity = '0'

			price = driver.find_element(By.CLASS_NAME, 'price').text.replace('£','')

			append_list_as_row(filepathHeaderCSV, [brand, name, link[1], panel_size, 'UK', stock, available, quantity, date, supplier, prod_link, price, quantity])
			time.sleep(3)
		except Exception:
			print('[Alternergy] ['+link[1]+'] - ' + str(cnt)+'/'+str(len(prod_links))+' - SKIP')
		cnt+=1

driver.quit()
##################################################################################################################
print('UPLOADING NOW...')

name = 'Alternergy'
num = '19'

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


