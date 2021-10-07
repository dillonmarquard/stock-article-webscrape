# stock-webcrawl
Collect stock related articles for analysis and price prediction
## Requirements
- Python (3.7.9)
- requests
- requests-html
- datetime
- pandas
- pickle
- bs4 (BeautifulSoup)
## Current State
- Collects links from first page of Google search "<stock-tag> news on:<date(YYYY-MM-DD)>"
- Collects html from each link
- Parse html for text
- Dictionary by date for each stock
  - stock tag
  - text data from html
  - stock price percent change
  - date    

Notice that the data for each day is independently wrapped into a data_wrapper class for independent storage.
This makes it easier to preserve large quantities of data by date for each stock.  
## To-Do
- Develop NLP pipeline
  - clean text data
  - create bag of relevant words 
    - find words correlated to changes in stock price
- create embedding to reduce dimension of one-hot encoded vector
- using spatial analysis techniques to gain a better understanding of the embedding
- find a good model to predict price changes from the embedding
- write paper?
## Notes
- Example implementation of Current State in main.py
