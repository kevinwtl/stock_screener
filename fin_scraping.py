import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
#TODO: 1) Add thousand separator into the numbers. 2) Turn transposing into the last action to be performed. 3) Apply to_numeric to all columns (before transposing)

def single_table_scraped(url, table_class):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text,'lxml')

    table = soup.find('table',class_ = table_class)

    table.find_all('tr')[0].find_all('td')[0].text.strip() # first date

    title_list = []
    items_list = []

    for row in table.find_all('tr'): # scrape the table
        try:
            items = [row.find_all('td')[col].text.strip().replace(',','') for col in range(1,6)] # remove thousand separator
        except:
            items = []

        try:
            title = row.find_all('td')[0].text.strip() # Title
        except:
            title = np.nan
            items = []

            # try:
            #     for i, item in enumerate(items):
            #         items[i] = float(item)
            # except:
            #     pass
        #except:
            #item = []
        title_list.append(title)
        items_list.append(items)

    df = pd.DataFrame(items_list, index = title_list).dropna().T # TODO reset index so that duplicates do not cause error
    
    df.replace('-','0',inplace=True) #replace '-' with zero

    return df

def all_pages_scraped(ticker, period = "annual"):
    merged_df = pd.DataFrame()

    tabs = ['financial-ratios', 'profit-loss', 'cash-flow', 'balance-sheet', 'earnings-summary'] # 5 sub-tabs to scrape

    for tab in tabs:
        url = "http://www.aastocks.com/en/stocks/analysis/company-fundamental/" + tab + "?symbol=" + ticker + "&period=4" # TODO: annual vs interim
        if tab == 'profit-loss' or tab == 'balance-sheet': # There are 2 tables on these 2 tabs
            df = single_table_scraped(url, "cnhk-cf tblM s4 s5 type2 mar15T")
            df = df.join(single_table_scraped(url, "cnhk-cf tblM s4 s5 mar15T"), how = 'outer',)
        else: # Only 1 table on other tabs
            df = single_table_scraped(url, "cnhk-cf tblM s4 s5 type2 mar15T")

        merged_df = merged_df.join(df, how = 'outer', rsuffix=' (duplicated)')

    # Make 'Closing Date' index & Transpose
    merged_df = merged_df.T
    merged_df.columns = merged_df.iloc[0]
    merged_df = merged_df[1:]

    # Remove rows with rsuffix: 'duplicated'
    merged_df = merged_df[~merged_df.index.str.contains('duplicated')]

    # Reset Index
    merged_df.reset_index(inplace = True)

    # Rename rows that are named 'Others' for clarity
    l = list(merged_df[merged_df['index'] == 'Others'].index)
    merged_df.loc[l[0]].iloc[0] = 'Others (Net Cash Flow from Return on Investments & Servicing of Finance)'
    merged_df.loc[l[1]].iloc[0] = 'Others (Net Cash Flow from Investing Activities)'
    merged_df.loc[l[2]].iloc[0] = 'Others (Net Cash Flow from Financing Activities)'

    # Make the 'index' column to become index again TODO:
    merged_df.index = merged_df['index']
    merged_df = merged_df.iloc[:,1:]

    return merged_df


#df = all_pages_scraped('2660')
#df.to_csv('2660.csv')

