from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from sklearn.pipeline import Pipeline

text_clf = Pipeline([
     ('vect', CountVectorizer()),
     ('tfidf', TfidfTransformer()),
     ('clf', MultinomialNB()),
    ])
class Model:
    def __init__(self,data):
        self.cVectorizer = CountVectorizer()
        self.cVectorizer.fit(data)
        pass
    def preprocess(self,data):
        data = self.cVectorizer.transform(data)
        
