import pandas as pd

file = input() # Expecting Yahoo Finance Headers
data = pd.read_csv(file)
data['percent_change'] = (data['Close'] - data['Open']) / data['Open']
data.to_csv(file,index=False)
