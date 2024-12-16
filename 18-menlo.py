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
password = 'Energy4321!'


def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeaderCSV = 'final-menlo.csv'
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


driver.get('https://www.shop.menloelectric.com/en/login?back=my-account')
time.sleep(3)

driver.find_element(By.ID, 'c-p-bn').click()
time.sleep(3)

driver.find_elements(By.CLASS_NAME, "form-control")[0].send_keys(username)
driver.find_elements(By.CLASS_NAME, "form-control")[1].send_keys(password)
driver.find_element(By.CLASS_NAME, "form-control-submit").click()
time.sleep(3)

ws = driver.get_window_size()
# driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')

links = [['https://www.shop.menloelectric.com/en/10-solar-panels', 'Module'],
		['https://www.shop.menloelectric.com/en/11-solar-inverters', 'Inverter'],
		['https://www.shop.menloelectric.com/en/100-solar-battery-storage', 'Battery'],
		['https://www.shop.menloelectric.com/en/14-solar-accessories', 'Accessory']]

for link in links:
	pg = 1
	print('Menlo '+link[1]+' Page '+str(pg))
	driver.get(link[0])
	time.sleep(2)

	nxtPg = 0
	urls = []
	while nxtPg == 0:
		prods = driver.find_elements(By.CLASS_NAME, 'product-miniature')
		for prod in prods:
			urls.append(prod.find_elements(By.TAG_NAME, 'a')[0].get_attribute('href'))

		if 'page-list' in driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML'):
			nxt = driver.find_element(By.CLASS_NAME, 'pagination').find_elements(By.TAG_NAME, 'li')[-1]
			if 'next' in nxt.get_attribute('innerHTML'):
				pg+=1
				driver.get(nxt.find_element(By.TAG_NAME, 'a').get_attribute('href'))
				print('Menlo '+link[1]+' Page '+str(pg))
				time.sleep(3)
				nxtPg = 0
		print('Menlo '+link[1]+' Page DONE')
		nxtPg = 1


	totPg = driver.find_element(By.CLASS_NAME, 'product__quantity').text.split(' ')[1]
	for url in urls:
		print('[MENLO] ['+link[1]+'] - '+str(urls.index(url)+1)+'/'+str(len(urls)))
		driver.get(url)
		time.sleep(1)

		info = driver.find_element(By.ID, 'product-details').get_attribute('data-product')
		load = json.loads(info)

		brand = load['category_name']
		name = load['name']
		avail = load['availability']
		price = load['price_amount']
		prod_link = load['link']
		supplier = 'Menlo'

		if link[1] == 'Module':
			size = load['features'][2]['value']
		else:
			size = 0

		if avail == 'available':
			stock = 'Yes'
			available = '0'
			quantity = load['quantity']
		else:
			stock = '0'
			available = '0'
			quantity = '0'

		date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')


		append_list_as_row(filepathHeaderCSV, [brand, name, link[1], size , 'Poland', stock, available, quantity, date, supplier, prod_link, price, quantity])
driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'Menlo'
num = '26'

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






