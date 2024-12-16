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

def convert(number):
	if len(str(number)) == 4:
		decimal = pow(10,3)
		return number / decimal
	return number

filepathHeaderCSV = 'final-solar-traders.csv'
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
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--log-level=3')
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# make chrome log requests
agin = 0
while agin == 0:
	try:
		capabilities = DesiredCapabilities.CHROME
		capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # newer: goog:loggingPrefs
		# driver = webdriver.Chrome(options=options, desired_capabilities=capabilities, service=Service(ChromeDriverManager().install()))
		driver = webdriver.Chrome(options=options, desired_capabilities=capabilities, service = Service(executable_path="chromedriver.exe"))
		ws = driver.get_window_size()
		driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')
		# driver.get('https://solartraders.com/en/marketplace/login')
		# time.sleep(2)
		# driver.find_element(By.ID, 'user_email').send_keys('supply@solar-distribution-group.eu')
		# driver.find_element(By.ID, 'user_password').send_keys('ricpew-pyqGyv-jomgy2')
		# driver.find_element(By.CLASS_NAME, 'btn-primary').click()
		driver.get('https://www.solartraders.com/en/products')
		time.sleep(5)

		agin = 1
	except Exception:
		agin = 0

scroll = True
scroll_con = 0
while scroll:
	con = len(driver.find_elements(By.CLASS_NAME, 'flex-column')[1].find_elements(By.CLASS_NAME, 'card'))
	print('[SOLAR TRADER] Scrolling: '+str(scroll_con))
	if scroll_con == con:
		scroll = False
	else:
		scroll_con = con
		driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
		time.sleep(4)

logs_raw = driver.get_log("performance")
logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

def log_filter(log_):
	return (
		# is an actual response
		log_["method"] == "Network.responseReceived"
		# and json
		and "json" in log_["params"]["response"]["mimeType"]
	)

print('[SOLAR TRADER] Scraping...')
for log in filter(log_filter, logs):
	lp = 0
	while lp == 0:
		try:
			request_id = log["params"]["requestId"]
			jsn = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
			datas = json.loads(jsn['body'])['results'][0]['hits']
			lp = 1
		except Exception as e:
			print(str(e))
			time.sleep(5)
			lp = 0

	for data in datas:
		con = []
		con.append(data['producer_name'])
		con.append(data['product_name'])
		if data['offer_type'] == 'solar_module':
			con.append('Module')
		elif data['offer_type'] == 'inverter':
			con.append('Inverter')
		elif data['offer_type'] == 'accessory':
			con.append('Accessory')
		elif data['offer_type'] == 'battery':
			con.append('Battery')

		if data['offer_type'] == 'solar_module':
			if str(data['length']) == 'None' or str(data['width']) == 'None' or str(data['thickness']) == 'None':
				con.append('0')
			else:
				ps = "{:,}".format(data['length'])+' x '+"{:,}".format(data['width'])+' x '+str(data['thickness'])
				con.append(ps.replace(',',''))

		else:
			con.append('0')
		con.append(pycountry.countries.get(alpha_2=data['offer']['location']).name)
		if data['offer']['in_stock']:
			con.append('Yes')
			con.append('0')
		else:
			con.append('0')
			con.append(str(time.mktime(datetime.fromtimestamp(data['offer']['available_starting_at_ts']).date().timetuple())))

		try:
			con.append(data['offer']['quantity'])
		except Exception as e:
			pass

		now = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
		con.append(now)
		con.append('Solar Traders')
		con.append('https://www.solartraders.com/en/marketplace/offers/'+str(data['slug']))

		try:
			con.append(data['offer']['price_ranges'][0]['price_per_quantity'])
		except Exception as e:
			pass

		try:
			con.append(data['offer']['min_quantity'])
		except Exception as e:
			pass

		append_list_as_row(filepathHeaderCSV, con)
print('[SOLAR TRADER] Done Scraping')
driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'SOLAR_TRADERS'
num = '2'

if platform.system() == 'Windows':
	loc = 'G:\\Other computers\\My MacBook Air\\Intelligen\\'+filepathHeaderCSV
elif platform.system() == 'Darwin':
	loc = '/Users/b2y/Work/Intelligen/'+filepathHeaderCSV

options = Options()
# options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized')
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