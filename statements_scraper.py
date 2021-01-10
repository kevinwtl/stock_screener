import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np

#TODO: 1) Turn transposing into the last action to be performed. 2) Apply to_numeric to all columns (before transposing)

def company_name(ticker):
    resp = requests.get('http://www.aastocks.com/en/stocks/analysis/company-fundamental/basic-information?symbol=' + ticker)
    soup = BeautifulSoup(resp.text,'lxml')
    table = soup.find('table',class_ = 'cnhk-cf tblM s4 s5 mar15T')
    comp_name = table.find_all('tr')[0].find_all('td')[1].text
    return comp_name

def share_issued(ticker):
    resp = requests.get('http://www.aastocks.com/en/stocks/analysis/company-fundamental/basic-information?symbol=' + ticker)
    soup = BeautifulSoup(resp.text,'lxml')
    table = soup.find('table',class_ = 'cnhk-cf tblM s4 s5 mar15T')
    shares_issued = int(table.find_all('tr')[9].find_all('td')[1].text.replace(',',''))
    return shares_issued

def scrape_table(url, table_class):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text,'lxml')

    table = soup.find('table',class_ = table_class)

    title_list = []
    items_list = []

    for row in table.find_all('tr'): # scrape the table
        try:
            items = [row.find_all('td')[col].text.strip().replace(',','') for col in range(1,len(row.find_all('td')))] # remove thousand separator
        except:
            items = []

        try:
            title = row.find_all('td')[0].text.strip() # Title
        except:
            title = np.nan
            items = []

        title_list.append(title)
        items_list.append(items)

    df = pd.DataFrame(items_list, index = title_list).dropna().T # TODO: reset index so that duplicates do not cause error
    
    df.replace('-','0',inplace=True) #replace '-' with zero

    return df

def scrape_statements(ticker , period = "annual"):
    
    ticker = str(int(ticker))
    
    merged_df = pd.DataFrame()

    tabs = ['financial-ratios', 'profit-loss', 'cash-flow', 'balance-sheet', 'earnings-summary'] # 5 sub-tabs to scrape

    # Scrape data
    for tab in tabs:
        url = "http://www.aastocks.com/en/stocks/analysis/company-fundamental/" + tab + "?symbol=" + ticker + "&period=4" # TODO: annual vs interim
        df = scrape_table(url, "cnhk-cf tblM s4 s5 type2 mar15T")
        try:
            df = df.join(scrape_table(url, "cnhk-cf tblM s4 s5 mar15T"), how = 'outer') # if there are second table
        except: # Only 1 table on other tabs
            pass
        merged_df = merged_df.join(df, how = 'outer', rsuffix=' (duplicated)')

    
    # Skips companies with "No related information"
    if len(merged_df) == 0 or "No related information." in merged_df.columns:
        pass
    else:
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
        merged_df = merged_df.drop(columns = ['Trend']).replace('',np.nan).dropna(axis=1)
        merged_df.index.name = company_name(ticker)
        merged_df.loc['Share Issued (Share)'] = share_issued(ticker)
        
        # Turn all the strings into numerics
        merged_df = merged_df.apply(pd.to_numeric,errors='ignore',axis=1)

        return merged_df

df = scrape_statements('4614') # Test Case
