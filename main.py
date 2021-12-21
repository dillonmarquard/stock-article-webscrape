from datetime import date

from Stock import *

s = date(2020,1,1)
e = date(2021,1,1)
tesla = Stock("tsla")
#tesla.load_data()
tesla.add_data_range(s,e,stockpath='pricedata/tsla.csv')
tesla.save_data()

# adding individual days
#tesla.add_data(s)
#tesla.add_stock_data(s,stockpath='pricedata/tsla.csv')

