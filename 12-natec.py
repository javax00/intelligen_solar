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
password = 'ytW6xvQRkb'

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-natec.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-natec.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_data_available', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
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
# options.add_argument("--start-maximized")
options.add_argument('--disable-infobars')
options.add_argument("--disable-extensions")
options.add_argument('--window-size=1920,1080')
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

err = 0
while err == 0:
	try:
		# driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
		driver = webdriver.Chrome(options=options, service = Service(executable_path="chromedriver.exe"))
		driver.implicitly_wait(5)
		# driver.minimize_window()
		ws = driver.get_window_size()
		driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')
		err = 1
	except Exception:
		err = 0
		time.sleep(5)

driver.get('https://clientportal.natec.com/en/login')
time.sleep(5)

driver.find_element(By.ID, 'username').send_keys(username)
driver.find_element(By.ID, 'password').send_keys(password)
driver.find_elements(By.CLASS_NAME, 'checkbox__check')[0].click()
driver.find_elements(By.CLASS_NAME, 'checkbox__check')[1].click()
driver.find_element(By.CLASS_NAME, 'new-button').click()
time.sleep(5)

driver.get('https://clientportal.natec.com/front/prijzen')
time.sleep(5)

# driver.find_element(By.CLASS_NAME, 'left').find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')[-1].click()
driver.find_element(By.XPATH, '//*[@id="filter"]/div/div[1]/div').find_elements(By.CLASS_NAME, 'inputSet')[-1].click()
time.sleep(5)

cats = ['Solar panels',
		'Inverters',
		'Inverter accessories',
		'Batteries',
		'Battery accessories']

# cats = ['Solar panels']

for cs in cats:
	cat = driver.find_element(By.XPATH, '//*[@id="filter"]/div/div[1]/div').find_elements(By.CLASS_NAME, 'inputSet')
	for c in cat:
		if cs == c.text:
			c.click()
			time.sleep(10)

			scl = 0
			while scl == 0:
				try:
					driver.find_element(By.CLASS_NAME, 'load-more-btn').click()
					time.sleep(6)
					scl = 0
				except Exception as e:
					scl = 1

			items = driver.find_element(By.ID, 'items_table').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
			for item in items:
				name = item.find_element(By.CLASS_NAME, 'description').text
				brand = name.split(' ')[0]
				if cs == 'Solar panels':
					catg = 'Module'
				elif cs == 'Inverters':
					catg = 'Inverter'
				elif cs == 'Batteries':
					catg = 'Battery'
				elif cs == 'Inverter accessories':
					catg = 'Accessory'
				elif cs == 'Battery accessories':
					catg = 'Accessory'

				location = 'Netherlands'
				date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
				supplier = 'Natec'

				at = item.find_element(By.CLASS_NAME, 'td-description').get_attribute('innerHTML')
				if 'item-extra--warning' in at:
					avail_text = item.find_element(By.CLASS_NAME, 'item-extra--warning').text
				else:
					avail_text = ''


				if 'Datasheet' in item.text:
					try:
						prod_link = item.find_element(By.CLASS_NAME, 'glink').get_attribute('href')
					except Exception as e:
						prod_link = ''
				else:
					prod_link = ''

				p = item.find_elements(By.TAG_NAME, 'strong')[-1].text.replace('€','')
				price = p.split(',')[0].replace('.',',')+'.'+p.split(',')[1]

				append_list_as_row(filepathHeaderCSV, [brand, name, catg, '0', location, '0', '0', '0', avail_text, date, supplier, prod_link, price, '0'])

				print('[NATEC] ['+catg+'] - '+str(items.index(item)+1)+':'+str(len(items)))

driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'NATEC'
num = '15'

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