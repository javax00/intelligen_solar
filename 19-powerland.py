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

filepathHeaderCSV = 'final-powerland.csv'
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

links = [['https://www.powerland.co.uk/collections/solar-panels-1', 'Module'],
		['https://www.powerland.co.uk/collections/inverters', 'Inverter'],
		['https://www.powerland.co.uk/collections/battery-storage', 'Battery'],
		['https://www.powerland.co.uk/collections/solar-panel-fitting-mounting-kits', 'Accessory']]

# links = [['https://www.powerland.co.uk/collections/solar-panels-1', 'Module']]

driver.get('https://www.powerland.co.uk')
time.sleep(3)
if 'ez-cookie-notification__accept' in driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML'):
	driver.find_element(By.ID, 'ez-cookie-notification__accept').click()
	time.sleep(1)

for link in links:
	driver.get(link[0])
	time.sleep(5)

	driver.find_element(By.CLASS_NAME, 'l4vw').find_elements(By.TAG_NAME, 'a')[-1].click()
	time.sleep(2)

	nxtPg = 0
	urls = []
	countProds = 1
	while nxtPg == 0:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)

		prods = driver.find_elements(By.CLASS_NAME, 'w20')
		for prod in prods:
			size = ''
			if link[1] == 'Module':
				info = prod.find_element(By.CLASS_NAME, 'info').text
				if 'Reference' in info:
					a = info.split('Reference')[1]
					b = a.split('Length:')[1][:6].strip()
					c  = a.split('Width:')[1][:6].strip()
					if 'Depth:' in a:
						d  = a.split('Depth:')[1][:3].strip()
						size = b+' x '+c+' x '+d
					else:
						size = b+' x '+c
				else:
					a = info
					if 'Height:' in a:
						b = a.split('Height:')[1][:6].strip()
						c  = a.split('Width:')[1][:6].strip()
						if 'Depth:' in a:
							d  = a.split('Depth:')[1][:3].strip()
							size = b+' x '+c+' x '+d
						else:
							size = b+' x '+c

			stock = '0'
			available = '0'
			quantity = '0'

			getStock = prod.find_element(By.CLASS_NAME, 'static')
			if 'mobile-hide' in getStock.get_attribute('innerHTML'):
				getStock = getStock.find_element(By.CLASS_NAME, 'mobile-hide').text.split(' / ')[0]
				if 'In Stock' == getStock:
					stock = 'Yes'

			title = prod.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a')
			brand = title.text.split(' ')[0]
			name = title.text.replace(brand+' ', '')
			prod_link = title.get_attribute('href')
			price = prod.find_element(By.CLASS_NAME, 'price_new').find_element(By.TAG_NAME, 'span').text.replace('£','')
			date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
			supplier = 'Powerland'

			totalProds = driver.find_elements(By.TAG_NAME, 'h2')[0].text.split(' ')[0]

			print('[POWERLAND] ['+link[1]+'] - '+str(countProds)+'/'+totalProds)
			append_list_as_row(filepathHeaderCSV, [brand, name, link[1], size , 'UK', stock, available, quantity, date, supplier, prod_link, price, quantity])
			countProds+=1


		nxt = driver.find_elements(By.TAG_NAME, 'ol')[1].find_elements(By.TAG_NAME, 'li')[-1]
		if 'Next' in nxt.get_attribute('innerHTML'):
			driver.get(nxt.find_element(By.TAG_NAME, 'a').get_attribute('href'))
			nxtPg = 0
		else:
			nxtPg = 1
driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'Powerland'
num = '27'

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






