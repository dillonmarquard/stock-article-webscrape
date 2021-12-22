import pandas as pd
from requests_html import HTMLSession
from datetime import date, timedelta
import numpy as np
import progressbar

from Crawler import Crawler

blacklist = ['youtube','bloomberg','wikipedia','wsj']

class Stock:
    def __init__(self,tag):
        self.tag = tag
        self.df = pd.DataFrame(columns=["tag","date","link","percent_change","text"])
    
    def add_data(self,date):
        spooder = Crawler()
        response = spooder.request(self.tag,date)
        
        links = spooder.extract_links(response)
        for link in links:
            if sum([link.find(domain) for domain in blacklist]) != -1*len(blacklist):
                continue
            response = spooder.request(self.tag,date,link)
            if response == None:
                continue
            self.df.loc[len(self.df.index)] = [self.tag,str(date),link,pd.NA,spooder.extract_text(response)]

    def add_stock_data(self,date,stockpath):
        info = pd.read_csv(stockpath)
        if len(info.loc[info['Date'] == str(date)]['percent_change'].values) > 0:
            self.df.loc[self.df['date'] == str(date), 'percent_change'] = np.float(info.loc[info['Date'] == str(date)]['percent_change'].values)

    def get_data(self,date):
        return self.df.loc[self.df['date'] == str(date)]
    
    def save_data(self):
        self.df.to_csv("{}.csv".format(self.tag),index=False)
        print("done saving ${} data.".format(self.tag))

    def load_data(self):
        self.df = pd.read_csv("{}.csv".format(self.tag))
        print("done loading ${} data.".format(self.tag))

    def add_data_range(self,date_start,date_end,stockpath=None):
        if stockpath != None:
            info = pd.read_csv(stockpath)
        widgets = [
                ' [', progressbar.Timer(), '] ',
                progressbar.Percentage(), ' ',
                progressbar.Bar(),
                ' (', progressbar.ETA(), ') ',
            ]
        bar = progressbar.ProgressBar((date_end-date_start).days+1,widgets=widgets).start()
        date = date_start
        while date < date_end:
            self.add_data(date)
            # print(date)
            if stockpath != None:
                if len(info.loc[info['Date'] == str(date)]['percent_change'].values) > 0:
                    self.df.loc[self.df['date'] == str(date), 'percent_change'] = np.float(info.loc[info['Date'] == str(date)]['percent_change'].values)
            date += timedelta(days=1)
            bar.update((date-date_start).days)
        print('done adding ${} data in range.'.format(self.tag))
