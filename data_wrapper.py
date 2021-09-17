from datetime import date

class data_wrapper:
    def __init__(self,tag,data,date,pChange=None):
        self.tag = tag
        self.date = date
        self.pChange = pChange
        self.data = data
