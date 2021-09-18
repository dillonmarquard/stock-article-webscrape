import os
from os import listdir
import requests
from requests_html import HTMLSession
from datetime import date, timedelta
from bs4 import BeautifulSoup
import pickle

from Stock import *
from Crawler import *


s = date(2021,9,1)
e = date(2021,9,16)
tesla = Stock("tsla")
#tesla.load_data()
tesla.fill_data_range(s,e)
# This is your preferred method of collecting large amount of data
# If you choose to use Stock::add_data() you will need to use Stock::load_pChange() to load the stock price data into the data_wrapper
# and save using Stock::save_data()
# To convince you Stock::fill_data_range() only needs to read the <stock-tag>.csv once


