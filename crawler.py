import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

from requests_html import HTMLSession # html-only sessions for faster scraping, but lose out on JS loaded content

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait

import re
import json
import time
from tqdm import tqdm

# Error Definitions
class MaxRecursionError(Exception):
    def __str__(self):
        return f'MaxRecursionError {self.url}'
    def __init__(self,url:str):
        self.url = url
class ArticleNotFoundError(Exception):
    def __str__(self):
        return 'ArticleNotFoundError'
    def __init__(self):
        pass
class AccessDeniedError(Exception):
    def __str__(self):
        return 'AccessDeniedError'
    def __init__(self):
        pass
class NotAccessibleError(Exception):
    def __str__(self):
        return 'NotAccessibleError'
    def __init__(self):
        pass
class LinkParseError(Exception):
    def __str__(self):
        return 'LinkParseError'
    def __init__(self):
        pass

# API Client for webscraping article data
class APIClient:
    def __str__(self):
        return f'Chrome Webscraper {self.driver} ({self.chrome_driver_version})'
    
    def __init__(self):
        # html-only session
        self.session = HTMLSession()

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
        chrome_options.add_experimental_option("prefs", { 
            "download_restrictions":3,"download.open_pdf_in_system_reader": False,
            "download.prompt_for_download": True,
            "download.default_directory": "/dev/null",
            "plugins.always_open_pdf_externally": False })
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36'
        chrome_options.add_argument('user-agent={0}'.format(user_agent))
        self.chrome_driver_version = ChromeDriverManager().install()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

        # default timeout for page load
        self.driver.set_page_load_timeout(5) # 8 for consistency, 4 for speed

        # recursion setup for auto-retry
        self.MAX_DEPTH = 1
        self.API_WAIT_SECONDS = 5

        # blacklisted link patterns ie: yahoo finance
        self.link_blacklist = ['finance.yahoo','sec.gov','money.cnn','markets.businessinsider.com','google.com','marketwatch.com','github.com','youtube.com','fintel.io','detroitnews.com','xml-sitemap']

        # configured lists
        self.not_found_titles = ['not*.found','404','can*.t*.find'] # all lower-case; any acceptable re pattern
    ##################################
    ##################################
    
    # API
    def get_stock_data(self,tag:str,date:str,num_links:int=25,progress=False):
        tmpdf = pd.DataFrame(columns=['date','tag','link','title','raw_html'])
        tmplinks = self.get_google_links(tag,date,num_links)
        
        if progress: # to update progress bar for testing
            rng = tqdm(range(len(tmplinks)))
        else:
            rng = range(len(tmplinks))
        for i in rng:
            try:
                tmpdata = self.get_article_data(tmplinks[i])
                if tmpdata != None:
                    tmpdata['date'] = date
                    tmpdata['tag'] = tag
                    tmpdf = pd.concat((tmpdf,pd.DataFrame([tmpdata],columns=['date','tag','link','title','raw_html'])),axis=0)
            except Exception as e:
                print('Error:',e) # parse error, ignore fault
        return tmpdf
    
    def get_google_links(self,tag:str,date:str,num_links:int=25,recursion_depth=1):
        # Extract links from google search
        # Input: tag, date, num_links
        # Output: list of URLs
        url = "https://www.google.com/search?q={}+news+on%3A{}&num={}".format(tag,date,num_links)
        try:
            tmp = self.session.get(url).html.absolute_links
            res = self.filter_links(tmp)
        except:
            if recursion_depth <= self.MAX_DEPTH: # depth check for successive retry
                res = self.get_google_links(tag,date,recursion_depth=recursion_depth+1)
            else:
                raise MaxRecursionError(url)
        return res
    
    def get_article_data(self,url:str,recursion_depth=1):
        # Extract info from article
        # Input: URL
        # Output: article data json
        try:
            if recursion_depth == 1:
                html = self.get_html_from_url(url)
            else:
                html = self.get_js_html_from_url(url)
            data = {}
            data['link'] = url
            data['title'] = self.get_title(html)
            
            if max(map(lambda pattern : len(re.findall(pattern, data['title'].lower())), self.not_found_titles)):
                raise ArticleNotFoundError
            elif max(map(lambda pattern : len(re.findall(pattern, data['title'].lower())), ['access+denied'])):
                raise AccessDeniedError
            data['raw_html'] = html # preserve raw format for subsequent analysis to potentially extract more data
            # data['text'] = self.get_text_v1_0(html) # method for extracting text data from html v1.0
            return data
        except:
            if recursion_depth <= self.MAX_DEPTH: # depth check for successive retry
                time.sleep(self.API_WAIT_SECONDS) # prevent api throttling on failure
                data = self.get_article_data(url,recursion_depth=recursion_depth+1) # try js on html-only failure
            else:
                raise MaxRecursionError(url)
    
    ##################################
    ##################################

    # Webdriver
    def get_js_html_from_url(self,url:str):
        try:
            self.driver.get(url)
            return self.driver.page_source
        except:
            raise NotAccessibleError

    def get_html_from_url(self,url:str):
        # https://requests.readthedocs.io/projects/requests-html/en/latest/
        # requests-html is now trying to support js, but we will explore the capabilities later
        try:
            res = self.session.get(url)
            return res.text
        except:
            raise NotAccessibleError    

    # HTML Processing Helper functions
    def get_text_v1_0(self,html:str):
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

    # only load JS when absolutely necessary to be more efficient and avoid throttling
    # def get_links(self,html:str): 
    #     soup = BeautifulSoup(html, 'html.parser')
    #     links = []
    #     for x in soup.find_all('a'):
    #         try:
    #             tmp = x['href'].replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
    #             if 'https://' == tmp[0:8] and min([re.findall(pattern,tmp) == [] for pattern in self.link_blacklist]): # check for blacklisted pattern
    #                 links += [tmp]
    #         except:
    #             pass # parse error, ignore fault; bad data
    #     return links

    def filter_links(self,unfiltered:list):
        links = []
        for x in unfiltered:
            try:
                tmp = x.replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
                if 'https://' == tmp[0:8] and min([re.findall(pattern,tmp) == [] for pattern in self.link_blacklist]): # check for blacklisted pattern
                    links += [tmp] # only add non-blacklisted urls
            except:
                raise LinkParseError # parse error, ignore fault; bad data
        return links

    def __del__(self):
        self.driver.close()
