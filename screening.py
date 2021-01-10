import os
os.chdir('/Users/tinglam/Documents/GitHub/stock_screener')
import rating
import pandas as pd
from statements_scraper import scrape_statements, company_name
import shelve
pd.options.mode.chained_assignment = None 
pd.options.display.float_format = "{:,.2f}".format
db_path = 'database'
db = shelve.open(db_path)
stock_list = list(pd.read_csv('stock_list.csv')['ticker'])




## Screen for ROIC > 20% over past 3 years

threshold = 30
my_dict = {}

for ticker in stock_list:
    try:
        data = db[str(ticker)]
    except KeyError:
        data = scrape_statements(str(ticker))
        db[str(ticker)] = data # Update db

        
    try:
        ROIC = data.loc['Net Profit'] / (data.loc['Total Equity'] + data.loc['Total Debt'] - data.loc['Cash & Cash Equivalents at End of Year']) * 100
        if ROIC[-1] > threshold and ROIC[-2] > threshold and ROIC[-3] > threshold:
            weighted_ROIC = rating.weighted_average(ROIC)
            my_dict[ticker] = weighted_ROIC
    except:
        pass
    
db.close()
    
    
df = pd.DataFrame.from_dict(my_dict,orient='index')