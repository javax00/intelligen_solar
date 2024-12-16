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
import pytz
import time
import json
import glob
import os

link = []
# ['PVXCHANGE', '5']
# ataya oy

approve = [['VDH_SOLAR', '8'],
			['HADEC', '13'],
			['LIBRA', '14'],
			['PVXCHANGE', '5'], # FOR DELETE
			['BAYWA', '7'],
			['SOLAR_TRADERS', '2'],
			['KRANNICH', '6'],
			['SECONDSOL', '4'],
			['NATEC', '15'],
			['MEMODO', '10'],
			['ALTERNERGY', '19'],
			['SEGENSOLAR', '16']]

files = glob.glob("G:\\Other computers\\My MacBook Air\\Intelligen\\*.csv")
# files = glob.glob("/Users/b2y/Work/Intelligen/*.csv")
list_of_files = sorted(files, key=lambda x: os.stat(x).st_size, reverse=True)
for x in list_of_files:
	a = x.split('final-')[1].replace('.csv','').replace('-','_').upper()
	for y in approve:
		if a == y[0]:
			temp = y
			temp.insert(2, x)
			link.append(temp)
			break

options = Options()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--log-level=3')

err = 0
while err == 0:
	try:
		# driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
		driver = webdriver.Chrome(options=options, service = Service(executable_path="chromedriver.exe"))
		driver.implicitly_wait(10)
		driver.get('https://xsolarx.com/')
		err = 1
	except Exception:
		err = 0
		time.sleep(5)
time.sleep(2)

driver.find_element(By.ID, 'edit-name').send_keys('glennkarlnavarra008@gmail.com')
driver.find_element(By.ID, 'edit-pass').send_keys('Navarra12321!')
driver.find_element(By.CLASS_NAME, 'form-submit').click()
time.sleep(2)

for x in link:
	agin = 0
	while agin == 0:
		driver.get('https://xsolarx.com/feed/'+x[1]+'/edit')
		time.sleep(2)

		# UNLOCK AND SAVE
		body = driver.find_element(By.TAG_NAME, 'body').text
		if 'Unlock and Save' in body:
			driver.find_elements(By.CLASS_NAME, 'form-submit')[1].click()
			time.sleep(2)
			driver.get('https://xsolarx.com/feed/'+x[1]+'/edit')
			time.sleep(2)

		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'edit-plugin-fetcher-source-remove-button'))).click()
		time.sleep(2)

		driver.find_element(By.CLASS_NAME, 'form-file').send_keys(x[2])
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
				if 'has been updated' in body:
					done = 1
					agin = 1
					print('['+str(link.index(x)+1)+'/'+str(len(link))+'] '+str(x[0])+' - done\n')
				elif 'Fetching:' in body:
					print('['+str(link.index(x)+1)+'/'+str(len(link))+'] '+str(x[0])+' - '+str(c*5)+'secs - upload...')
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



