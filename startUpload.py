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

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # newer: goog:loggingPrefs
# driver = webdriver.Chrome(desired_capabilities=capabilities, service=Service(ChromeDriverManager().install()))
driver = webdriver.Chrome(service = Service(executable_path="chromedriver.exe"))
driver.quit()

# os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 1-solar_trader.py"')      # 

os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 2-pvxchange.py"')         # GOOD
time.sleep(5)
os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 3-secondsol.py"')         # GOOD
time.sleep(5)
# os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 4-baywa.py"')             # GOOD
time.sleep(5)
os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 5-krannich.py"')          # GOOD
time.sleep(5)
# os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 6-vdh_solar.py"')         # GOOD
time.sleep(5)
# os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 9-memodo.py"')            # GOOD
time.sleep(5)
os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 10-hadec.py"')            # GOOD
time.sleep(5)
os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 11-libra.py"')            # GOOD
time.sleep(5)
# os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 12-natec.py"')            # GOOD
time.sleep(5)
# os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 14-estg.py"')             # GOOD
time.sleep(5)
os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 15-solarclarity.py"')     # GOOD
time.sleep(5)
os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 16-alternergy.py"')       # GOOD
time.sleep(5)
# os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 17-keno.py"')             # GOOD
time.sleep(5)
os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 18-menlo.py"')             # GOOD
time.sleep(5)
# os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 19-powerland.py"')             # GOOD
time.sleep(5)
os.system('start cmd.exe /k "mode con cols=63 lines=70 & G: & cd \\"Other computers\\My MacBook Air\\Intelligen\\" & python 13-segensolar.py"')       # GOOD