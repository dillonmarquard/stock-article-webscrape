import os
from os import listdir
import requests
from requests_html import HTMLSession
from datetime import date, timedelta
from bs4 import BeautifulSoup
import pickle

from Stock import *
from Crawler import *


s = date(2021,1,1)
e = date(2021,9,16)
tesla = Stock("tsla")
tesla.load_data()
#tesla.load_pChange()
#tesla.add_data(d)
#tesla.fill_data_range(s,e)
#tesla.save_data()

