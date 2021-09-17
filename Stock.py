import os
from os import listdir
from requests_html import HTMLSession
from datetime import date, timedelta
import pickle # save collected data
import pandas as pd

from Crawler import Crawler
from data_wrapper import data_wrapper

class Stock:
    def __init__(self,tag):
        self.tag = tag
        self.data_dict = {} # index data by date
        
    def add_data(self,date):
        if date.weekday() > 4:
            return
        spooder = Crawler()
        response = spooder.request(self.tag,date)
        
        links = spooder.extract_links(response)
        for link in links:
            response = spooder.request(self.tag,date,link)
            if response == None:
                continue
            if str(date) not in self.data_dict:
                self.data_dict[str(date)] = data_wrapper(self.tag,spooder.extract_text(response),date)
            else:
                self.data_dict[str(date)].data = self.data_dict[str(date)].data + spooder.extract_text(response)
            
    def get_data(self,date): # returns a data wrapper for the specified day
        if str(date) not in self.data_dict:
            return None
        else:
            return self.data_dict[str(date)]

    def save_data(self,date=None): # save data_wrappers as rawbytes with pickle
        if date == None:
            for key in self.data_dict:
                with open("{}/{}".format(self.tag,key),'wb') as f:
                    pickle.dump(self.data_dict[key],f)
        else:
            with open("{}/{}".format(self.tag,str(date)),'wb') as f:
                pickle.dump(self.data_dict[str(date)],f)
        print('done saving data.')
            
    def load_data(self):
        for s_date in listdir(self.tag):
            i_date = s_date.split('-')
            d = date(int(i_date[0]),int(i_date[1]),int(i_date[2]))
            with open("{}/{}".format(self.tag,s_date),'rb') as f:
                if s_date not in self.data_dict:
                    self.data_dict[s_date] = pickle.load(f)
        print('done loading data.')
        
    def fill_data_range(self,date_start,date_end): # preferred method for creating training data
        date = date_start
        already_collected = listdir("{}/".format(self.tag))
        self.load_data()
        while date < date_end:
            if str(date) not in already_collected and date.weekday() < 5:
                self.add_data(date)
                print(date)
            date += timedelta(days=1)
        self.load_pChange()
        self.clean_wrapper()
        self.save_data()
        print('done filling data.')
        
    def load_pChange(self):
        stock_data = pd.read_csv("pricedata/{}.csv".format(self.tag))
        for key in self.data_dict.keys():
            a = list(stock_data[stock_data['Date'] == key].get('pChange').values)
            if a == []:
                a = None
            else:
                a = a[0]
            self.data_dict[key].pChange = a
        print('done loading price data.')

    def clean_wrapper(self): # remove data without pChange values
        for key in list(self.data_dict.keys()):
            if self.data_dict[key].pChange == None:
                self.data_dict.pop(key)
                try:
                    os.remove("{}/{}".format(self.tag,key))
                except:
                    continue
