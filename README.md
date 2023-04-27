# stock-webcrawl
Collect stock related articles to predict changes in price utilizing natural language processing.
## Requirements
- Python (3.9.4)
- requests
- requests-html
- datetime
- pandas
- bs4 (BeautifulSoup)
## Current State
- Collects 25 links from first page of Google search "<stock-tag> news on:<date(YYYY-MM-DD)>" ignoring certain blacklisted sights that require auth
- Collects html from each link
- Parse html for paragraph text
- DataFrame for each stock (each row is a link)
  - tag
  - date
  - link url
  - percent change
  - text data
- Classifier to predict based on bag of relevant words
## To-Do
- Develop NLP pipeline
- Vectorize words with embedding, then vectorize corpora.
  - Use spatial analysis techniques to classify articles and their impact on market direction (binary: increase or decrease)
## Notes
- Example implementation of Current State in main.py
 
## Suggestions
  
1. Once you have the articles related to a given stock by given dates, you could break them down into unigrams and perform frequency analysis in relation to the stock's rise or fall.  This should lead to some interesting visuals.

2. A little more advanced.  You could take the above articles and their unigrams, but also combine a sentiment feature depending on whether the article is positive or negative or both.  It would be more valuable to perform sentiment analysis by each sentence in the articles and perform cumulation.

3. Even more advanced and tricky.  While you have articles about a stock, it's likely that the author meanders around to other topics.  So the trick would be to focus only on commentary related to the specific stock or company of interest.  In that case, you would need to perform some type of named "entity" recognition (NER) to zero in on particular comments rather than all of the article.
