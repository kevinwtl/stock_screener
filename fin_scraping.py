import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np

def single_table_scraped(url, table_class):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text,'lxml')

    table = soup.find('table',class_ = table_class)

    table.find_all('tr')[0].find_all('td')[0].text.strip() # first date

    title_list = []
    items_list = []

    for row in table.find_all('tr'): # scrape the table
        try:
            items = [row.find_all('td')[col].text.strip().replace(',','') for col in range(1,6)]
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
    

    return df

def all_pages_scraped(ticker, period = "annual"):
    merged_df = pd.DataFrame()

    tabs = ['financial-ratios', 'profit-loss', 'cash-flow', 'balance-sheet', 'earnings-summary']

    for tab in tabs:
        url = "http://www.aastocks.com/en/stocks/analysis/company-fundamental/" + tab + "?symbol=" + ticker + "&period=4" # TODO: annual vs interim
        if tab == 'profit-loss' or tab == 'balance-sheet':
            df = single_table_scraped(url, "cnhk-cf tblM s4 s5 type2 mar15T")
            df.join(single_table_scraped(url, "cnhk-cf tblM s4 s5 mar15T"), how = 'outer')
        else:
            df = single_table_scraped(url, "cnhk-cf tblM s4 s5 type2 mar15T")

        merged_df = merged_df.join(df, how = 'outer', rsuffix=' (duplicated)')

    # Turn 'Closing Date' into index & Transpose
    merged_df = merged_df.T
    merged_df.columns = merged_df.iloc[0]
    merged_df = merged_df[1:]

    # Remove rows with 'duplicate'
    merged_df = merged_df[~merged_df.index.str.contains('duplicated')]

    # Reset Index
    merged_df.reset_index(inplace = True)

    # Rename rows that are called 'Others'
    l = list(merged_df[merged_df['index'] == 'Others'].index)
    merged_df.loc[l[0]].iloc[0] = 'Others (Net Cash Flow from Return on Investments & Servicing of Finance)'
    merged_df.loc[l[1]].iloc[0] = 'Others (Net Cash Flow from Investing Activities)'
    merged_df.loc[l[2]].iloc[0] = 'Others (Net Cash Flow from Financing Activities)'



    return merged_df



#df = all_pages_scraped('0005')
