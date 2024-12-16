from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
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
import getpass
import gspread
import pytz
import math
import time
import json
import os

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-greenside.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-greenside.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://www.greensideenergy.com/panels?skip=0', 'Module'],
		['https://www.greensideenergy.com/inverters?skip=0', 'Inverter'],
		['https://www.greensideenergy.com/inverter-accessories?skip=0', 'Accessory'],
		['https://www.greensideenergy.com/energy-storage?skip=0', 'Battery']]

# links = [['https://www.greensideenergy.com/inverters?skip=0', 'Inverter']]

s, i, a, b = [], [], [], []
s.append(fHeader)
i.append(fHeader)
a.append(fHeader)
b.append(fHeader)

for link in links:
	#########
	options = Options()
	options.add_argument("--headless")
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-gpu')
	options.add_argument('start-maximized')
	options.add_argument('disable-infobars')
	options.add_argument("--disable-extensions")
	options.add_argument('--window-size=1920,1080')
	options.add_argument('--ignore-certificate-errors-spki-list')
	options.add_argument('--log-level=3')

	# make chrome log requests
	agin = 0
	while agin == 0:
		try:
			capabilities = DesiredCapabilities.CHROME
			capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # newer: goog:loggingPrefs
			driver = webdriver.Chrome(options=options, desired_capabilities=capabilities, service=Service(ChromeDriverManager().install()))
			agin = 1
		except Exception:
			agin = 0
	#########

	driver.get(link[0])
	time.sleep(5)
	totalPage = driver.find_elements(By.CLASS_NAME, 'ant-pagination-item')[-1].text

	clk = 1
	while int(totalPage) > clk:
		print(link[1]+' = '+str(clk)+'/'+totalPage)

		logs_raw = driver.get_log("performance")
		logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

		def log_filter(log_):
			return (
				# is an actual response
				log_["method"] == "Network.responseReceived"
				# and json
				and "json" in log_["params"]["response"]["mimeType"]
			)

		temp1 = ''
		for log in filter(log_filter, logs):
			temp1 = ''
			lp = 0
			while lp == 0:
				try:
					request_id = log["params"]["requestId"]
					jsn = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
					if 'masterProducts' in str(jsn['body']):
						temp1 = json.loads(jsn['body'])['data']['masterProducts']
					lp = 1
				except Exception as e:
					print('ERROR: Trying again. '+str(e))
					time.sleep(5)
					lp = 0

			if temp1 != '':
				datas = temp1

		for data in datas['result']:
			brand, name, panel_size, date, supplier, prod_link = '', '', '', '', '', ''
			for d in data:
				try:
					brand = data['manufacturer']['name']
				except Exception as e:
					brand = ''
				name = data['name']
				if link[1] == 'Module':
					try:
						p = json.loads(data['options'])
						panel_size = p['depth']+' x '+p['width']+' x '+p['height']
					except Exception:
						panel_size = ''
				else:
					panel_size = ''
				date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
				supplier = 'Greenside'
				prod_link = 'https://www.greensideenergy.com/solar/'+data['slug']

			append_list_as_row(filepathHeaderCSV, [brand, name, link[1], panel_size, '0', '0', '0', '0', date, supplier, prod_link, '0', '0'])

		url = driver.current_url.split('=')
		driver.get(url[0]+'='+str(int(url[1])+48))
		time.sleep(8)
		clk+=1
	print(link[1]+' = '+str(clk)+'/'+totalPage)
	driver.quit()

# ~~~~

# dic = []
# allData = s[1:]+i[1:]+a[1:]+b[1:]
# c = 0
# for data in allData:
# 	temp = {}
# 	temp['brand'] = data[0]
# 	temp['name'] = data[1]
# 	temp['category'] = data[2]
# 	temp['panel_size'] = data[3]
# 	temp['location'] = data[4]
# 	temp['stock'] = data[5]
# 	temp['quantity'] = data[6]
# 	temp['date'] = data[7]
# 	temp['supplier'] = data[8]
# 	temp['link'] = data[9]
# 	dic.append(temp)

# final = []
# tot = int(str((len(dic)-1)/50).split('.')[0])
# for fifty in range(1, tot+1):
# 	final.append({'items': dic[(fifty*50)-50: fifty*50]})
# if len(dic) > tot*50:
# 	final.append({'items': dic[tot*50:]})

# requests.delete('https://portal.xsolarx.com/api/products/Greenside')
# print('Greenside - DELETED')
# time.sleep(3)

# cnt = 1
# for x in final:
# 	url = 'http://portal.xsolarx.com/api/products'
# 	r = requests.post(url, headers={'content-type': 'application/json'}, data=json.dumps(x))
# 	print(str(cnt)+'-'+str(len(final))+': '+str('Good' if r.status_code == 200 else 'Bad'))
# 	cnt += 1

# ~~~~
# gc = gspread.service_account(filename='/Users/b2y/Work/Intelligen/credentials/solar-trader-9411c909622f.json')
# sh = gc.open("Inventory & Availability")

# ws = sh.worksheet('Greenside')
# col = len(ws.col_values(1))
# # ws.delete_rows(1,len(col)-1)
# sh.values_clear("Greenside!A2:J"+str(col))

# # ALL IN 1 TAB
# col = ws.col_values(1)
# ws.update('A2', s[1:]+i[1:]+a[1:]+b[1:])
# ~~~~

# new_header = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
# df = pd.DataFrame(s[1:]+i[1:]+a[1:]+b[1:], columns=new_header)
# writer = pd.ExcelWriter(filepathHeader, engine='openpyxl')
# df.to_excel(writer, sheet_name='Baywa US', index=False)

# writer.save()


