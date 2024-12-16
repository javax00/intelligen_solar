from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
from csv import writer
from time import sleep
import pandas as pd
import requests
import gspread
import random
import pytz
import time
import json
import os

def append_list_as_row(file_name, list_of_elem):
	with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
		csv_writer = writer(write_obj)
		csv_writer.writerow(list_of_elem)

filepathHeader = 'final-baywa-US.xlsx'
fHeader = ['Brand', 'Name', 'Category', 'Panel Size', 'Location', 'Stock', 'Quantity', 'Date', 'Supplier', 'Link']

filepathHeaderCSV = 'final-baywa-US.csv'
fHeaderCSV = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
try:
	os.remove(filepathHeaderCSV)
	time.sleep(1)
except Exception as e:
	pass
append_list_as_row(filepathHeaderCSV, fHeaderCSV)

links = [['https://solar-store-us.baywa-re.com/products/category/solar-panels', 'Module'],
		['https://solar-store-us.baywa-re.com/products/category/inverters', 'Inverter'],
		['https://solar-store-us.baywa-re.com/products/category/inverter-accessories', 'Accessory'],
		['https://solar-store-us.baywa-re.com/products/category/storage-products', 'Battery']]

manuf = {'HQC': 'Q Cells',
		'JA': 'JA Solar',
		'LG': 'LG',
		'LNG': 'LONGi',
		'MIN': 'Mission Solar',
		'PNS': 'Panasonic',
		'REC': 'REC',
		'SIL': 'Silfab',
		'TRI': 'Trina Solar',
		'EN': 'Enphase',
		'FRO': 'Fronius',
		'SB': 'SMA',
		'SBS': 'SMA',
		'SE': 'Solar Edge',
		'APSM': 'APsmart',
		'CCS': 'CCS',
		'BYD': 'BYD',
		'GEN': 'Generac',
		'LGC': 'LG'}

# links = [['https://solar-store-us.baywa-re.com/products/category/solar-panels', 'Module']]

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
		driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
		driver.implicitly_wait(10)
		err = 1
	except Exception:
		err = 0
		time.sleep(5)


s, i, a, b = [], [], [], []
s.append(fHeader)
i.append(fHeader)
a.append(fHeader)
b.append(fHeader)

for link in links:
	driver.get(link[0])
	time.sleep(5)

	print(link[1])

	try:
		driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
	except Exception:
		pass

	tot = driver.find_element(By.CLASS_NAME, "facets-facet-browse-title").get_attribute('data-quantity')

	urls = []
	nxtPg = 0
	while nxtPg == 0:
		prodRows = driver.find_elements(By.CLASS_NAME, "facets-items-collection-view-row")
		for prodRow in prodRows:
			prods = prodRow.find_elements(By.CLASS_NAME, "facets-items-collection-view-cell-span6")
			for prod in prods:
				urls.append(prod.find_element(By.CLASS_NAME, "facets-item-cell-table-link-image").get_attribute('href'))

		try:
			driver.find_element(By.CLASS_NAME, "global-views-pagination-next").find_element(By.TAG_NAME, "a").click()
			time.sleep(5)
			nxtPg = 0
		except Exception:
			nxtPg = 1

	final = []
	count = 1
	for url in urls:
		print(str(count)+'-'+tot)
		again = 0
		while again == 0:
			try:
				driver.get(url)
				time.sleep(3)
				driver.implicitly_wait(10)

				brand = manuf[driver.find_element(By.CLASS_NAME, "product-details-full-content-header-title").text.split('-')[0]]
				name = driver.find_element(By.CLASS_NAME, "product-details-full-content-header-title").text
				sps = driver.find_elements(By.ID, "detailed_desc")[2].find_elements(By.TAG_NAME, 'li')
				if link[1] == 'Module':
					for sp in sps:
						if 'Shipping Dimensions' in sp.text:
							panel_size = sp.text.split(': ')[1].replace(' in', '')
				else:
					panel_size = 0

				try:
					for sp in sps:
						if 'Pallet Qty' in sp.text:
							if int(sp.text.split(': ')[1]) != 0:
								stock = 'Yes'
								quantity = sp.text.split(': ')[1]
							else:
								stock = 0
								quantity = 0
				except Exception:
					stock = 0
					quantity = 0
				date = datetime.now().replace(tzinfo=pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
				supplier = 'BayWa r.e. US'
				prod_link = url

				if name == '':
					again = 0
				else:
					again = 1
					append_list_as_row(filepathHeaderCSV, [brand, name, link[1], panel_size, '0', stock, '0', quantity, date, supplier, prod_link, '0', '0'])
					if link[1] == 'Module':
						s.append([brand, name, link[1], panel_size, '0', stock, '0', quantity, date, supplier, prod_link, '0', '0'])
					elif link[1] == 'Inverter':
						i.append([brand, name, link[1], panel_size, '0', stock, '0', quantity, date, supplier, prod_link, '0', '0'])
					elif link[1] == 'Accessory':
						a.append([brand, name, link[1], panel_size, '0', stock, '0', quantity, date, supplier, prod_link, '0', '0'])
					elif link[1] == 'Battery':
						b.append([brand, name, link[1], panel_size, '0', stock, '0', quantity, date, supplier, prod_link, '0', '0'])
				driver.get('data:,')
			except Exception as e:
				print(e)
				again = 0
				break
		count+=1
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

# requests.delete('https://portal.xsolarx.com/api/products/BayWa r.e. US')
# print('BayWa r.e. US - DELETED')
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

# ws = sh.worksheet('BayWa r.e. US')
# col = len(ws.col_values(1))
# # ws.delete_rows(1,len(col)-1)
# sh.values_clear("BayWa r.e. US!A2:J"+str(col))

# # ALL IN 1 TAB
# col = ws.col_values(1)
# ws.update('A2', s[1:]+i[1:]+a[1:]+b[1:])
# ~~~~

# new_header = ['field_manufacturer', 'title', 'field_category', 'field_module_size', 'field_location', 'field_stock', 'field_available', 'field_quantity', 'field_date_scraped', 'field_supplier', 'field_url', 'field_price', 'field_moq']
# df = pd.DataFrame(s[1:]+i[1:]+a[1:]+b[1:], columns=new_header)
# writer = pd.ExcelWriter(filepathHeader, engine='openpyxl')
# df.to_excel(writer, sheet_name='Baywa US', index=False)

# writer.save()


