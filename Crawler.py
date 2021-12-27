from os import listdir
import requests
from requests_html import HTMLSession
from datetime import date
from bs4 import BeautifulSoup
import re

class Crawler:
    def __init__(self):
        self.session = HTMLSession()
        
    def request(self,tag,date,url=None):
        # returns html of search result
        
        if url == None: # by default finds links to relevant websites
            url = "https://www.google.com/search?q={}+news+on%3A{}&num={}".format(tag,str(date),15) # num is the number of links google gives on the search page
        try: # for scraping data from relevant links
            response = self.session.get(url)
            return response
        except:
            return None
    
    def extract_text(self,response):
        # extracts text from html
        data = []
        page = BeautifulSoup(response.text,'html.parser')
        text_arr = page.find_all('p')
        data = []
        for a in text_arr:
            g = a.text
            g = re.sub('[.]+',' ',g)
            g = re.sub('[^a-zA-z ]+','',g)
            g = re.sub('\s+', ' ', g)
            if len(g.split()) > 15:
                #print(len(g),g)
                data.append(g)
        data = "".join(data)
        return data
        
    def extract_links(self,response):
        # extracts links from html
        links = []
        page = BeautifulSoup(response.text,'html.parser')
        text_arr = page.find_all('a')
        #print(text_arr)
        for a in text_arr:
            g = a.get("href")
            if g == None:
                continue
            if g.find("https") != -1 and g.find("google") == -1:
                links.append(g)
        return links
