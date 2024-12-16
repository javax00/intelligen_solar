from selenium import webdriver
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
# https://www.secondsol.com/en/system/login.htm

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

def has_numbers(inputString):
	return any(char.isdigit() for char in inputString)

filepathHeader = 'final-secondsol.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-secondsol.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://www.secondsol.com/de/marketplace-search/pv-module.htm', 'Module'],
		['https://www.secondsol.com/de/marketplace-search/inverter.htm', 'Inverter'],
		['https://www.secondsol.com/de/marketplace-search/storage.htm', 'Battery']]

# links = [['https://www.secondsol.com/en/marktplatzfilter/?kat2=40957&kategorie=16&currentpage=1&level3=false', 'Battery']]

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

# driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()), desired_capabilities=caps)
driver = webdriver.Chrome(options=options, service = Service(executable_path="chromedriver.exe"))
driver.implicitly_wait(10)
# driver.minimize_window()
ws = driver.get_window_size()
driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')

s, i, a, b = [], [], [], []
s.append(fHeader)
i.append(fHeader)
a.append(fHeader)
b.append(fHeader)

loc = {
	"fi-de": "Germany",
	"fi-at": "Austria",
	"fi-fr": "France",
	"fi-us": "USA",
	"fi-it": "Italy",
	"fi-si": "Slovenia",
	"fi-pl": "Poland",
	"fi-ch": "Switzerland",
	"fi-cz": "Czechia",
	"fi-nl": "Netherlands",
	"fi-es": "Spain",
	"fi-ro": "Romania",
	"fi-be": "Belgium",
	"fi-lt": "Lithuania",
	"fi-gr": "Greece",
	"fi-cn": "China",
	"fi-lu": "Luxembourg",
	"fi-in": "India",
	"fi-bg": "Bulgaria",
}


for link in links:
	driver.get(link[0])
	time.sleep(2)

	try:
		driver.find_elements(By.CLASS_NAME, "btn-success-cookie-blue")[0].click()
	except Exception:
		pass


	nxtPg = 0
	cnt = 1
	while nxtPg == 0:
		time.sleep(4)
		prods = driver.find_element(By.ID, 'article-list').find_elements(By.CLASS_NAME, "article-col")
		cntP = 1
		for prod in prods:
			l,wd,we,price,stock,quantity,available = '','','','','','',''

			brand = prod.find_element(By.CLASS_NAME, 'mb-0').text
			name = prod.find_element(By.CLASS_NAME, 'product-name').text

			location = prod.find_element(By.CLASS_NAME, 'article-footer').find_elements(By.CLASS_NAME, 'col-6')[-1].find_element(By.TAG_NAME, 'span').get_attribute('class').split(' ')[1]

			pr = prod.find_element(By.CLASS_NAME, 'point-out').find_elements(By.TAG_NAME, 'p')[0].text.split(' ')
			for p in pr:
				if has_numbers(p) and ',00' in p:
					price = p.replace(',','.')
					break
				else:
					price = '0'

			qua = prod.find_element(By.CLASS_NAME, 'text-start').find_elements(By.TAG_NAME, 'p')[-1].text.split(' ')
			for q in qua:
				if has_numbers(q):
					stock = 'Yes'
					quantity = q
					available = '0'
					break
				else:
					stock = 'No'
					quantity = '0'
					available = '0'

			date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
			supplier = 'SecondSol'
			prod_link = prod.find_element(By.CLASS_NAME, 'article-image').find_element(By.TAG_NAME, 'a').get_attribute('href')




			if link[1] == 'Module':
				but = prod.find_element(By.CLASS_NAME, 'btn-secondary')
				driver.execute_script("arguments[0].scrollIntoView();", but)
				# time.sleep(1)
				driver.execute_script("arguments[0].click();", but)

				tbl = prod.find_element(By.TAG_NAME, 'table').find_elements(By.TAG_NAME, 'tr')
				for t in tbl:
					if 'länge' in t.text.lower():
						l = t.find_elements(By.TAG_NAME, 'td')[-1].text
						if has_numbers(l):
							l = l
						else:
							l = '0'

				tbl = prod.find_element(By.TAG_NAME, 'table').find_elements(By.TAG_NAME, 'tr')
				for t in tbl:
					if 'breite' in t.text.lower():
						wd = t.find_elements(By.TAG_NAME, 'td')[-1].text
						if has_numbers(wd):
							wd = wd
						else:
							wd = '0'

				tbl = prod.find_element(By.TAG_NAME, 'table').find_elements(By.TAG_NAME, 'tr')
				for t in tbl:
					if 'gewicht' in t.text.lower():
						we = t.find_elements(By.TAG_NAME, 'td')[-1].text
						if has_numbers(we):
							we = we
						else:
							we = '0'

				panel_size = l+' x '+wd+' x '+we
			else:
				panel_size = '0'


			locs = ''
			try:
				locs = loc[location]
			except Exception as e:
				print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
				print(location)
				print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')


			append_list_as_row(filepathHeaderCSV, [brand, name, link[1], panel_size, locs, stock, available, quantity, date, supplier, prod_link, price, quantity])

			tot = driver.find_element(By.CLASS_NAME, 'pagination-list').find_elements(By.TAG_NAME, 'li')[-2].text
			print('[SECONDSOL] ['+link[1]+'] - '+str(cntP)+'/25 - '+str(cnt)+'/'+tot)
			cntP+=1

		try:
			driver.find_element(By.CLASS_NAME, 'pagination-list').find_elements(By.TAG_NAME, 'li')[-1].find_element(By.TAG_NAME, 'button').click()
			nxtPg = 0
			cnt+=1
		except Exception:
			nxtPg = 1
			pass

driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'SECONDSOL'
num = '4'

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