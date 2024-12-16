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
username = 'Thijs@getalpha.nl'
password = 'zegde5-dakkyv-Depkaw'

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-memodo.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-memodo.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://www.memodo-shop.com/solarpanels', 'Module'],
		['https://www.memodo-shop.com/inverters/', 'Inverter'],
		['https://www.memodo-shop.com/accessories-electrical/', 'Accessory'],
		['https://www.memodo-shop.com/home-storage/', 'Battery']]

# links = [['https://www.memodo-shop.com/solarpanels', 'Module']]

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

# driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
driver = webdriver.Chrome(options=options, service = Service(executable_path="chromedriver.exe"))
# driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)
# driver.minimize_window()
ws = driver.get_window_size()
driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')

s, i, a, b = [], [], [], []
s.append(fHeader)
i.append(fHeader)
a.append(fHeader)
b.append(fHeader)

driver.get('https://www.memodo-shop.com/account/login')
time.sleep(5)
driver.find_element(By.CLASS_NAME, 'cookie-permission--accept-all-button').click()
time.sleep(1)

if 'btn-close' in driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML'):
	driver.find_element(By.CLASS_NAME, 'btn-close').click()

# ERROR CREDENTIALS
driver.find_element(By.XPATH, '/html/body/div[1]/section/div/div/div[2]/div/div/form/div[2]/input').send_keys(username)
driver.find_element(By.XPATH, '/html/body/div[1]/section/div/div/div[2]/div/div/form/div[3]/input').send_keys(password)
driver.find_element(By.XPATH, '/html/body/div[1]/section/div/div/div[2]/div/div/form/div[5]/button').click()
time.sleep(10)

for link in links:
	driver.get(link[0])
	time.sleep(5)

	try:
		driver.find_element(By.CLASS_NAME, "modal-close").click()
		time.sleep(2)
	except Exception as e:
		pass

	try:
		driver.find_element(By.CLASS_NAME, "cookie-permission--accept-button").click()
		time.sleep(2)
	except Exception:
		pass

	scroll = 0
	cnt = 1
	while scroll == 0:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight*.8);")
		time.sleep(.5)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight*.9);")
		time.sleep(.5)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

		try:
			driver.find_element(By.CLASS_NAME, "js--loading-indicator")
			time.sleep(.5)
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight*.8);")
			time.sleep(.5)
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight*.9);")
			time.sleep(.5)
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			scroll = 0
			time.sleep(2)
		except Exception:
			try:
				driver.find_element(By.CLASS_NAME, "js--load-more").click()
				time.sleep(.5)
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight*.8);")
				time.sleep(.5)
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight*.9);")
				time.sleep(.5)
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				scroll = 0
				time.sleep(2)
			except Exception:
				driver.execute_script("window.scrollTo(0, 0);")
				time.sleep(2)
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight*.8);")
				time.sleep(.5)
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight*.9);")
				time.sleep(.5)
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				scroll = 1
		try:
			print('[MEMODO] ['+link[1]+'] - '+str(cnt)+'/'+str(driver.current_url).split('=')[1]+' - scrolling')
			if cnt >= 100:
				driver.delete_all_cookies()
				driver.get('https://www.memodo-shop.com')
				time.sleep(2)
				driver.refresh()
				time.sleep(2)
				driver.get(link[0])
				cnt = 1
		except Exception as e:
			pass
		cnt+=1
	print('Done Scrolling...')

	prods = driver.find_elements(By.CLASS_NAME, "product--box")
	for prod in prods:
		print('[MEMODO] ['+link[1]+'] - '+str(prods.index(prod)+1)+':'+str(len(prods)))
		try:
			brand = prod.find_element(By.CLASS_NAME, 'product-box--manufacturer').text.replace('Manufacturer: ', '')
			name = prod.find_element(By.CLASS_NAME, "product--title").text
			prod_link = prod.find_element(By.CLASS_NAME, 'product--image').get_attribute('href')
			date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
			supplier = 'Memodo'
			panel_size = ''
			if link[1] == 'Module':
				for y in prod.find_elements(By.CLASS_NAME, 'is--bold'):
					if 'Dimensions:' in y.text:
						panel_size = y.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, 'td')[1].text.replace('×','x')
			price = prod.find_elements(By.CLASS_NAME, 'product--price')[0].text.replace('€ *','')
			if ' ' in price:
				price = price.split(' ')[1]
			stock = '0'
			available = '0'
			if 'delivery--message' in prod.get_attribute('innerHTML'):
				stock_data = prod.find_element(By.CLASS_NAME, 'delivery--message').text
				if 'Available from stock' in stock_data:
					stock = 'Yes'
				else:
					nd = stock_data.split('.')
					d = datetime(int(nd[2]), int(nd[1]), int(nd[0]), 0, 0, 0)
					available = str(int(d.replace(tzinfo=timezone.utc).timestamp()))

			append_list_as_row(filepathHeaderCSV, [brand, name, link[1], panel_size, '0', stock, available, '0', date, supplier, prod_link, price, '0'])
		except Exception as e:
			print('No data')


driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'MEMODO'
num = '10'

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
		# driver = webdriver.Chrome(options=options)
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