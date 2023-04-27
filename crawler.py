import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import re
import json
import time
from tqdm import tqdm

# Error Definitions
class MaxRecursionError(Exception):
    def __init__(self):
        pass
class ArticleNotFoundError(Exception):
    def __init__(self):
        pass
class AccessDeniedError(Exception):
    def __init__(self):
        pass
class NotAccessibleError(Exception):
    def __init__(self):
        pass

# API Client for webscraping article data
class APIClient:
    def __str__(self):
        return f'Chrome Webscraper {self.driver} ({self.chrome_driver_version})'
    
    def __init__(self):
        # webdriver setup
        chrome_options = Options()
        chrome_options.add_argument("start-maximized"); # https://stackoverflow.com/a/26283818/1689770
        chrome_options.add_argument("enable-automation"); # https://stackoverflow.com/a/43840128/1689770
        chrome_options.add_argument("--headless"); # only if you are ACTUALLY running headless
        chrome_options.add_argument("--no-sandbox"); # https://stackoverflow.com/a/50725918/1689770
        chrome_options.add_argument("--disable-dev-shm-usage"); # https://stackoverflow.com/a/50725918/1689770
        chrome_options.add_argument("--disable-browser-side-navigation"); # https://stackoverflow.com/a/49123152/1689770
        chrome_options.add_argument("--disable-gpu"); # https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_experimental_option("detach", True)
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36'
        chrome_options.add_argument('user-agent={0}'.format(user_agent))
        self.chrome_driver_version = ChromeDriverManager().install()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        self.driver.set_page_load_timeout(8)
        # recursion setup for auto-retry
        self.MAX_DEPTH = 3

        # blacklisted link patterns ie: yahoo finance
        self.link_blacklist = ['finance.yahoo','sec.gov','money.cnn','markets.businessinsider.com','google.com','marketwatch.com','github.com']

        # configured lists
        self.not_found_titles = ['not*.found','404','can*.t*.find'] # all lower-case; any acceptable re pattern
    ##################################
    ##################################
    
    # API
    def get_stock_data(self,tag:str,date:str,num_links:int=25):
        tmpdf = pd.DataFrame(columns=['date','link','title','text'])
        tmplinks = self.get_google_links(tag,date,num_links)
        
        for i in range(len(tmplinks)):
            try:
                tmpdata = self.get_article_data(tmplinks[i])
                if tmpdata != None:
                    tmpdata['date'] = date
                    tmpdf = pd.concat((tmpdf,pd.DataFrame([tmpdata],columns=['date','link','title','text'])),axis=0)
            except:
                pass # parse error, ignore fault
        return tmpdf

    def get_google_links(self,tag:str,date:str,num_links:int=25,recursion_depth=1):
        # Extract links from google search
        # Input: tag, date, num_links
        # Output: list of URLs
        url = "https://www.google.com/search?q={}+news+on%3A{}&num={}".format(tag,date,num_links)
        try:
            res = self.get_html_from_url(url)
            res = self.get_links(res)
        except:
            if recursion_depth <= self.MAX_DEPTH: # depth check for successive retry
                res = self.get_google_links(tag,date,recursion_depth=recursion_depth+1)
            else:
                raise MaxRecursionError
        return res
    
    def get_article_data(self,url:str,recursion_depth=1):
        # Extract info from article
        # Input: URL
        # Output: article data json
        try:
            html = self.get_html_from_url(url)
            data = {}
            data['link'] = url # self identifier
            data['title'] = self.get_title(html)
            
            if max(map(lambda pattern : len(re.findall(pattern, data['title'].lower())), self.not_found_titles)):
                raise ArticleNotFoundError
            elif max(map(lambda pattern : len(re.findall(pattern, data['title'].lower())), ['access+denied'])):
                raise AccessDeniedError
            data['text'] = self.get_text(html) # text data
            return data
        except:
            if recursion_depth <= self.MAX_DEPTH: # depth check for successive retry
                time.sleep(5) # prevent api throttling on failure
                data = self.get_article_data(url,recursion_depth=recursion_depth+1)
            else:
                raise MaxRecursionError
        
    ##################################
    ##################################

    # Webdriver
    def get_html_from_url(self,url:str):
        try:
            self.driver.get(url)
            return self.driver.page_source
        except:
            raise NotAccessibleError
        

    # HTML Processing Helper functions
    def get_text(self,html:str):
        soup = BeautifulSoup(html, 'html.parser')
        text = ''
        for tmp in [tmp.text for tmp in soup.find_all(['a','p','h','h1','h2'])]:
            if len(tmp) > 25:
                text += tmp + ' '
        text = re.sub('\s+',' ',text.replace('\n',' ').replace('\xa0',' ').replace('\'','’').replace('   ',' ').strip())
        return text

    def get_title(self,html:str):
        soup = BeautifulSoup(html, 'html.parser')
        res = re.sub('\s+',' ',soup.find_all('title')[0].text.replace('\n',' ').replace('\xa0',' ').replace('\'','’').replace('   ',' ').strip())
        return res

    def get_links(self,html:str):
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for x in soup.find_all('a'):
            try:
                tmp = x['href'].replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
                if 'https://' == tmp[0:8] and min([re.findall(pattern,tmp) == [] for pattern in self.link_blacklist]): # check for blacklisted pattern
                    links += [tmp]
            except:
                pass # parse error, ignore faults
        return links

    def __del__(self):
        self.driver.close()
