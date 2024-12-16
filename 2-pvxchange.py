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

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-pvxchange.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-pvxchange.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

def getLinkHeader():
	userIndex = ua = UserAgent().random

	global headers
	headers = {
		'dnt': '1',
		'upgrade-insecure-requests': '1',
		'User-Agent': userIndex,
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-user': '?1',
		'sec-fetch-dest': 'document',
		'referer': 'https://www.facebook.com/',
		'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
		'Updgrade-Insecure-Requests': '1',
	}

links = [['https://www.pvxchange.com/Solar-Modules', 'Module'],
			['https://www.pvxchange.com/Solar-Inverters', 'Inverter'],
			['https://www.pvxchange.com/Solar-Accessories', 'Accessory'],
			['https://www.pvxchange.com/Solar-Batteries', 'Battery']]

# links = [['https://www.pvxchange.com/Solar-Inverters', 'Inverter']]

s, i, a, b = [], [], [], []
s.append(fHeader)
i.append(fHeader)
a.append(fHeader)
b.append(fHeader)

getLinkHeader()
session = requests.Session()
response = session.get('https://www.pvxchange.com/navi.php?k=1&suche=&Sortierung=8&af=96#hfilter', headers=headers)
print('done setting total product display')
time.sleep(5)

# https://www.pvxchange.com/My-account
# tdepoel@leposolar.nl
# 1980LEPO&

for x in links:
	getLinkHeader()
	response = session.get(x[0], headers=headers)
	soup = BeautifulSoup(response.text, features='lxml')

	tot = soup.find("div", {"class": "et-product-list-filter-total"}).text.strip()


	# tot = soup.find("div", {"class": "s360-horizontal-filter-content"}).find("div", {"class": "h3"}).text
	pages = int(math.ceil(int(tot.split(' ')[0])/96))
	time.sleep(5)

	for y in range(1, pages+1):
		getLinkHeader()
		err = 0
		while err == 0:
			try:
				response = session.get(x[0]+'_s'+str(y)+'#products', headers=headers, timeout=30)
				err = 1
			except Exception as e:
				print('again')
				err = 0
				time.sleep(5)
		soup = BeautifulSoup(response.text, features='lxml')

		prods = soup.find("div", {"class": "layout-gallery"}).find_all("div", {"itemprop": "itemListElement"})
		for l in prods:
			con = []
			con.append(l.find("div", {"class": "et-item-box-manufacturer"}).text)
			con.append(l.find("div", {"class": "et-item-box-title"}).text.strip())
			con.append(x[1])
			if x[1] == 'Module':
				con.append(l.find_all("div", {"class": "price-area"})[0].find_all("span")[-1].text.replace(',', ''))
			else:
				con.append('0')
			con.append('0')
			try:
				qty = int(l.find_all("div", {"class": "price-area"})[1].find("span", {"class": "value"}).text)
				if qty != 0:
					con.append("Yes")
					con.append("0")
				else:
					con.append('0')
					con.append('0')
				con.append(qty)
			except Exception:
				con.append('0')
				con.append('0')
				con.append('0')
			now = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
			con.append(now)
			con.append('Pvxchange')
			con.append(l.find("a", {"class": "text-clamp-2"})["href"].strip())
			# con.append('https://www.pvxchange.com/'+l.find("h3", {"class": "title"}).find("a")["href"].strip())
			con.append('0')
			con.append('0')
			append_list_as_row(filepathHeaderCSV, con)

			if x[1] == 'Module':
				s.append(con)
			elif x[1] == 'Inverter':
				i.append(con)
			elif x[1] == 'Accessory':
				a.append(con)
			elif x[1] == 'Battery':
				b.append(con)
			# time.sleep(1)

		print('[PVXCHANGE] ['+x[1]+'] - '+str(y)+'/'+str(pages))
		time.sleep(2)

##################################################################################################################
print('UPLOADING NOW...')

name = 'PVXCHANGE'
num = '5'

if platform.system() == 'Windows':
	loc = 'G:\\Other computers\\My MacBook Air\\Intelligen\\'+filepathHeaderCSV
elif platform.system() == 'Darwin':
	loc = '/Users/b2y/Work/Intelligen/'+filepathHeaderCSV

options = Options()
options.add_argument("--headless")
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
		driver.minimize_window()
		driver.implicitly_wait(10)
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
			# print(body)
			time.sleep(5)
			c+=1
		except Exception as e:
			done = 0
			pass
driver.quit()
print('ALL DONE!')
