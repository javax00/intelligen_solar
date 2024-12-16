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
password = 'paskos-rIsnyn-5kukjo'


def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-baywa.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-baywa.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://solarshop.baywa-re.lu/products/category/solar-modules?show=48', 'Module'],
		['https://solarshop.baywa-re.lu/products/category/inverters?show=48', 'Inverter'],
		['https://solarshop.baywa-re.lu/products/category/system-accessories?show=48', 'Accessory'],
		['https://solarshop.baywa-re.lu/products/category/storage-systems?show=48', 'Battery']]

# links = [['https://solarshop.baywa-re.lu/products/category/solar-modules?show=48', 'Module']]

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

driver.get('https://solarshop.baywa-re.lu/sca-lux-2019-2/checkout.ssp?is=login&login=T&fragment=login-register#login-register')
time.sleep(5)

try:
	driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
except Exception:
	pass

driver.find_element(By.ID, "login-email").send_keys(username)
driver.find_element(By.ID, "login-password").send_keys(password)
driver.find_element(By.CLASS_NAME, "login-register-login-submit").click()
time.sleep(10)

for link in links:
	again = 0
	while again == 0:
		try:
			driver.get(link[0])
			time.sleep(7)
			again = 1
		except Exception as e:
			print('Error: reloading now...')
			time.sleep(5)
			again = 0

	again = 0
	while again == 0:
		try:
			tot = driver.find_element(By.CLASS_NAME, "facets-facet-browse-title").get_attribute('data-quantity')
			again = 1
		except Exception as e:
			print('again...')
			driver.get(link[0])
			time.sleep(7)
			again = 0

	urls = []
	nxtPg = 0
	while nxtPg == 0:
		prodRows = driver.find_elements(By.CLASS_NAME, "facets-items-collection-view-row")
		for prodRow in prodRows:
			prods = prodRow.find_elements(By.CLASS_NAME, "facets-items-collection-view-cell-span4")
			for prod in prods:
				urls.append(prod.find_element(By.CLASS_NAME, "facets-item-cell-grid-link-image").get_attribute('href'))

		try:
			driver.find_element(By.CLASS_NAME, "global-views-pagination-next").find_element(By.TAG_NAME, "a").click()
			time.sleep(5)
			nxtPg = 0
		except Exception:
			nxtPg = 1

	final = []
	count = 1
	for url in urls:
		print('[BAYWA] ['+link[1]+'] - '+str(count)+'/'+tot)
		again = 0
		c = 0
		while again == 0:
			try:
				driver.get(url)
				time.sleep(3)
				driver.implicitly_wait(10)

				try:
					brand = driver.find_element(By.CLASS_NAME, "position-7").find_element(By.TAG_NAME, "img").get_attribute('alt').replace('Manufacturer - ', '')
				except Exception:
					brand = driver.find_element(By.CLASS_NAME, "product-details-full-content-header-title").text.split(' ')[0]

				try:
					name = driver.find_element(By.CLASS_NAME, "product-details-full-content-header-title").text.replace(brand+' ', '')
				except Exception as e:
					time.sleep(5)
					name = driver.find_element(By.CLASS_NAME, "product-details-full-content-header-title").text.replace(brand+' ', '')

				category = link[1]
				if category == 'Module':
					cnt1 = 0
					cnt2 = 0
					infos = driver.find_elements(By.CLASS_NAME, "baywa-details-label")
					for info in infos:
						if 'Dimensions' in info.text:
							cnt2 = cnt1
						else:
							cnt1+=1
					panel_size = driver.find_elements(By.CLASS_NAME, "baywa-details-values")[cnt2].text.replace(',', '').replace(' cm', '')
				else:
					panel_size = '0'
				location = '0'

				stock, available, quantity = '0', '0', '0'
				avail = driver.find_element(By.CLASS_NAME, "availability-status").text
				if 'currently not available' in avail or 'Out of stock' in avail or 'Please call for availability' in avail or 'On Request' in avail or 'on request' in avail or 'Not yet' in avail or 'Agotado' in avail:
					stock = '0'
				elif 'No availability, next availability' in avail:
					temp = avail.split(' ')[-1].split('-')
					temp.insert(1, '-W')
					temp1 = ''.join(temp)
					temp2 = datetime.strptime(temp1 + '-1', "%Y-W%W-%w")
					available = datetime.timestamp(temp2)
				elif 'More than' in avail:
					stock = 'Yes'
					quantity = avail.split(' ')[2]
				elif 'available' in avail:
					stock = 'Yes'
					quantity = avail.split(' ')[0]
				else:
					print(avail)

				price = driver.find_elements(By.CLASS_NAME, "product-views-price-lead")[0].get_attribute('data-rate')

				date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
				supplier = 'BayWa r.e.'
				prod_link = url

				if name == '':
					again = 0
				else:
					again = 1
					append_list_as_row(filepathHeaderCSV, [brand, name, category, panel_size, location, stock, available, quantity, date, supplier, prod_link, price, quantity])
				driver.get('data:,')
			except Exception as e:
				print(str(e))
				print('again...')
				again = 0
				c+=1
				if c >= 10:
					print('skipping...')
					again = 1
		count+=1

driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'BAYWA'
num = '7'

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