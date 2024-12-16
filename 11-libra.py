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
import re

### LOGIN ###
username = 'thijs@getalpha.nl'
password = 'vovrob-nykPuc-5gucga'

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-libra.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-libra.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://shop.libra.energy/en_GB/category/solar/solar-modules', 'Module'],
		['https://shop.libra.energy/en_GB/category/solar/inverters', 'Inverter'],
		['https://shop.libra.energy/en_GB/category/solar/accessories', 'Accessory'],
		['https://shop.libra.energy/en_GB/category/storage/batteries', 'Battery']]

# links = [['https://shop.libra.energy/en/products/solar/solar-modules', 'Module']]

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
		driver.implicitly_wait(10)
		# driver.minimize_window()
		ws = driver.get_window_size()
		driver.set_window_position(ws['width'], ws['height'], windowHandle ='current')
		driver.get('https://shop.libra.energy/en_GB/login')
		time.sleep(1)
		driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
		driver.find_element(By.XPATH, '/html/body/div[2]/nvs-app/main/div/div/div[2]/div[1]/form/div[1]/div/div/nvs-input/input').send_keys(username)
		driver.find_element(By.XPATH, '/html/body/div[2]/nvs-app/main/div/div/div[2]/div[1]/form/div[2]/div/div/nvs-input/input').send_keys(password)
		driver.find_element(By.XPATH, "/html/body/div[2]/nvs-app/main/div/div/div[2]/div[1]/form/div[3]/nvs-button[2]").click()
		time.sleep(5)

		err = 1
	except Exception as e:
		print(str(e))
		err = 0
		time.sleep(5)
print('Done log in...')

s, i, a, b = [], [], [], []
s.append(fHeader)
i.append(fHeader)
a.append(fHeader)
b.append(fHeader)

for link in links:
	driver.get(link[0])
	driver.implicitly_wait(10)
	time.sleep(7)

	if 'fc_frame' in driver.find_element(By.TAG_NAME, 'html').get_attribute('innerHTML'):
		driver.execute_script("""
			var l = document.getElementById("fc_frame");
			l.parentNode.removeChild(l);
		""")
		time.sleep(2)

	c = 0
	cnt = 1
	while c == 0:
		try:
			# try:
			# 	driver.find_element(By.CLASS_NAME, 't-cart-delivery-date-warning').find_element(By.TAG_NAME, 'button').click()
			# 	time.sleep(5)
			# except Exception as e:
			# 	pass

			tot = int(driver.find_element(By.XPATH, '/html/body/div[1]/nvs-app/main/div[2]/div/div[2]/div/div[3]/div[1]/nvs-heading').text.split(' ')[0])
			if str(tot/9).split('.')[1] != '0':
				print('[LIBRA] ['+link[1]+'] - '+str(cnt)+'/'+str(int(str(tot/9).split('.')[0])+1))
			else:
				print('[LIBRA] ['+link[1]+'] - '+str(cnt)+'/'+str(int(str(tot/9).split('.')[0])))

			items = driver.find_elements(By.CLASS_NAME, 'o-product-card')
			for item in items:
				try:
					title = item.find_element(By.CLASS_NAME, 'nvs-heading').text
					brand = title.split(' ')[0].replace(',','')
					name = title

					if link[1] == 'Module':
						if 'x' not in title and '×' not in title:
							panel_size = '0'
						elif 'x' in title.split(', ')[-1] or '×' in title.split(', ')[-1]:
							panel_size = title.split(', ')[-1]
							if ',' in panel_size:
								panel_size = panel_size.split(',')[1]
						else:
							panel_size = title.split(', ')[-2]

						if panel_size != '0':
							pp = re.findall('[0-9]+', panel_size)
							panel_size = ' x '.join(pp)
					else:
						panel_size = '0'

					location = 'Netherlands'

					stock, available, quantity = '0', '0', '0'
					avail = item.find_element(By.CLASS_NAME, 'm-product-availability').text
					if 'from' in avail:
						new_date = avail.split(' ')[2].split('-')
						available = str(time.mktime(datetime.strptime(new_date[1]+' '+new_date[2]+' '+new_date[0], '%m %d %Y').date().timetuple()))
						quantity = avail.split('(')[1].split(' ')[0]
					elif 'Not available' in avail or 'Contact us' in avail:
						pass
					elif 'pieces available' in avail or 'pallets available' in avail or 'piece available' in avail or 'boxes available' in avail or 'Available' in avail:
						stock = 'Yes'
						quantity = avail.split(' ')[0]
					else:
						print('ERROR: '+avail)

					price = item.find_element(By.CLASS_NAME, 'm-product-price').text.replace('€','').replace('apiece','')
					prod_link = item.find_element(By.CLASS_NAME, 'app-link').get_attribute('href')
					date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
					supplier = 'Libra'

					append_list_as_row(filepathHeaderCSV, [brand, name, link[1], panel_size, location, stock, available, quantity, date, supplier, prod_link, price, quantity])
				except Exception as e:
					pass

			try:
				nxt = driver.find_elements(By.CLASS_NAME, 'm-pagination-item')[-1].find_element(By.CLASS_NAME, 'nvs-button')
				if 'Next' in nxt.text:
					driver.get('https://shop.libra.energy'+nxt.get_attribute('href'))
					time.sleep(2)
					driver.refresh()
					time.sleep(5)
					cnt+=1
					c = 0
				else:
					c = 1
			except Exception as e:
				c = 1
		except Exception as e:
			c = 1


driver.quit()

##################################################################################################################
print('UPLOADING NOW...')

name = 'LIBRA'
num = '14'

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