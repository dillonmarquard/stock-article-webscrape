from os import listdir
import requests
from requests_html import HTMLSession
from datetime import date
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self):
        self.session = HTMLSession()
        
    def request(self,tag,date,url=None):
        # returns html of search result
        
        if url == None: # by default finds links to relevant websites
            url = "https://www.google.com/search?q={}+news+on%3A{}".format(tag,str(date))
        try: # for scraping data from relevant links
            response = self.session.get(url)
            return response
        except:
            return None
    
    def extract_text(self,response):
        # extracts text from html
        data = []
        page = BeautifulSoup(response.text,'html.parser')
        text_arr = page.find_all('p',text=True)

        for a in text_arr:
            g = a.text
            if g != "" and len(g) > 15 and g.find('›') == -1 and g.find("https://") == -1 and (g.find('.') != -1 or g.find(',') != -1):
               data.append(g)
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
