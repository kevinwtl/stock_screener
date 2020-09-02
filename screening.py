
import os
os.chdir('/Users/tinglam/Documents/GitHub/value_investing')
import pandas as pd
from statements_scraper import all_pages_scraped

#database = pd.read_csv('2660.csv',index_col='index').dropna(axis = 1)
pd.options.mode.chained_assignment = None 

def value_to_score(value, classification = {}):
    """
    Parameters:
    classification: input a dictionary, in the format of lower boundary : score
    
    Output:
    return the score as float
    
    Example:
    value_to_score(0.31,{0:0,0.1:1,0.2:1.5,0.3:2.5,0.4:3.75,0.5:4.5,0.6:5}) --> return 2.5
    """
    for threshold in classification.keys():
        if threshold <= value:
            score = classification.get(threshold)
    return score

def weighted_average(row):
    row = row.astype('float')
    return row[-1] * 0.7 + row[-2] * 0.2 + row[-1] * 0.1

def standard_deviation(row):
    row = row.astype('float')
    return row.std()

def score_calculation(database):
    # Read the dataframe
    df = pd.DataFrame(columns=database.columns)
    df1 = pd.DataFrame(columns = ['Reference Value','Score','Weights','Weighted Score'], index = ['1a) Top Line Growth','1b) EBIT Growth','1c) Bottom Line Growth','2a) Profit Margin','2b) Stability of Profit Margin'\
        ,'2c) Sign of Operating CF','3a) ROE','3b) CROE','3c) Stability of Returns', '3d) Sign of FCF', '3e) Cash Reinvestment Rate','4a) Operating CF to Net Debt','4b) Net Debt to Equity'])
    df1['Weights'] = [5,10,10,10,5,1000,7,13,3,1000,7,15,15]


    # Part 1: Sales performance
    ## 1a) Top Line Growth
    df.loc['Turnover Growth (%)'] = database.loc['Total Turnover'].astype('float').pct_change() * 100
    value = weighted_average(df.loc['Turnover Growth (%)'])
    score = value_to_score(value,{-999:-3,-5:-1,0:0,10:1,20:1.5,30:2.5,40:3.75,50:4.5,60:5})

    df1['Reference Value'][0] = value
    df1['Score'][0] = score


    ## 1b) EBIT Growth
    df.loc['Operating Profit Growth (%)'] = database.loc['Operating Profit'].astype('float').pct_change() * 100
    value = weighted_average(df.loc['Operating Profit Growth (%)'])
    score = value_to_score(value,{-999:-3,0:0,10:1,20:1.5,30:2.5,40:3.75,50:4.5,60:5})

    df1['Reference Value'][1] = value
    df1['Score'][1] = score


    ## 1c) Bottom Line Growth
    df.loc['Net Profit Growth (%)'] = database.loc['Net Profit Growth (%)']
    value = weighted_average(df.loc['Operating Profit Growth (%)'])
    score = value_to_score(value,{-999:-3,0:0,5:1,10:2,20:3,30:4,40:5})

    df1['Reference Value'][2] = value
    df1['Score'][2] = score




    # Part 2: Earnings Quality
    ## 2a) Profit Margin
    df.loc['Net Profit Margin (%)'] = database.loc['Net Profit Margin (%)']
    value = weighted_average(df.loc['Net Profit Margin (%)'])
    score = value_to_score(value,{-999:-3,0:0,6:1,10:1.5,13:2.5,17:3.75,19:4.5,22:5})

    df1['Reference Value'][3] = value
    df1['Score'][3] = score


    ## 2b) Stability of Profit Margin
    df.loc['Net Profit Margin (%)'] = database.loc['Net Profit Margin (%)']
    value = standard_deviation(df.loc['Net Profit Margin (%)'])
    score = 5/3 if value < 5 else 0

    df1['Reference Value'][4] = value
    df1['Score'][4] = score


    ## 2c) Sign of Operating CF
    df.loc['Net Cash Flow from Operating Activities'] = database.loc['Net Cash Flow from Operating Activities']
    value = -1 if (df.loc['Net Cash Flow from Operating Activities'].astype(float) < 0).any() == True else 1
    score = -999 if value == -1 else 0

    df1['Reference Value'][5] = value
    df1['Score'][5] = score




    # Part 3: Profitability
    ## 3a) ROE
    df.loc['Return on Equity (%)'] = database.loc['Return on Equity (%)']
    value = weighted_average(df.loc['Return on Equity (%)'])
    score = value_to_score(value,{-999:-3,0:1,12:2,18:3,21:4,24:5})

    df1['Reference Value'][6] = value
    df1['Score'][6] = score


    ## 3b) CROE
    df.loc['Cash Return on Equity (%)'] = database.loc['Net Cash Flow from Operating Activities'].astype('float') / database.loc['Total Equity'].astype('float') * 100
    value = weighted_average(df.loc['Cash Return on Equity (%)'])
    score = value_to_score(value,{-999:-3,0:1,12:2,18:3,21:4,24:5})

    df1['Reference Value'][7] = value
    df1['Score'][7] = score


    ## 3c) Stability of Returns
    df.loc['Stability of Returns'] = database.loc['Net Profit Margin (%)']
    value = (standard_deviation(df.loc['Return on Equity (%)']) + standard_deviation(df.loc['Cash Return on Equity (%)'])) / 2
    score = 5/3 if value < 5 else 0

    df1['Reference Value'][8] = value
    df1['Score'][8] = score


    ## 3d) Sign of FCF
    df.loc['CapEx'] = database.loc['Fixed Assets'].astype('float').diff()
    df.loc['FCF'] = database.loc['Net Cash Flow from Operating Activities'].astype('float') - df.loc['CapEx']
    value = -1 if (df.loc['FCF'].astype(float) < 0).any() == True else 1
    score = -999 if value == -1 else 0

    df1['Reference Value'][9] = value
    df1['Score'][9] = score

    ## 3e) Cash Reinvestment Rate
    df.loc['Cash Reinvestment Rate'] = df.loc['CapEx'].astype('float') / database.loc['Net Cash Flow from Operating Activities'].astype('float') * 100
    value = weighted_average(df.loc['Cash Reinvestment Rate'])
    score = value_to_score(value,{-999:5,0:4,10:3,20:2,35:1,50:0})

    df1['Reference Value'][10] = value
    df1['Score'][10] = score


    # Part 4: Solvency
    ## 4a) Operating CF to Net Debt
    df.loc['Net Debt'] = database.loc['Total Debt'].astype('float') - database.loc['Cash & Cash Equivalents at End of Year'].astype('float')
    df.loc['Operating CF to Net Debt'] = database.loc['Net Cash Flow from Operating Activities'].astype('float') / df.loc['Net Debt']
    value = weighted_average(df.loc['Operating CF to Net Debt'])
    score = value_to_score(value,{-999:5,0:4,3:3,4:2,6:1,8:0})

    df1['Reference Value'][11] = value
    df1['Score'][11] = score

    ## 4b) Net Debt to Equity
    df.loc['Net Debt to Equity'] = df.loc['Net Debt'] / database.loc['Total Equity'].astype('float')
    value = weighted_average(df.loc['Net Debt to Equity'])
    score = value_to_score(value,{-999:5,0:4,15:3,30:2,45:1,55:0})

    df1['Reference Value'][12] = value
    df1['Score'][12] = score




    # Part 5: Calculate scores
    df1['Weighted Score'] = df1['Score'] / 5 * df1['Weights']
    
    return df, df1

ticker = ' '
while ticker != '':
    ticker = input('Please Input the Ticker: ')
    database = all_pages_scraped(str(ticker))
    df,df1 = score_calculation(database)

    print(df1)
    print('Total Score: ' + str(df1['Weighted Score'].sum()))