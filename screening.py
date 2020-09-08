import os
os.chdir('/Users/tinglam/Documents/GitHub/value_investing')
import pandas as pd
from statements_scraper import scrape_statements, company_name
pd.options.mode.chained_assignment = None 
pd.options.display.float_format = "{:,.2f}".format


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
    return row[-1] * 0.7 + row[-2] * 0.2 + row[-1] * 0.1

def standard_deviation(row):
    return row.std()

def score_calculation(ticker):
    # Read the dataframe
    database = scrape_statements(str(ticker))
    summary_df = pd.DataFrame(columns=database.columns)
    score_df = pd.DataFrame(columns = ['Reference Value','Score','Weights','Weighted Score'], index = ['1a) Top Line Growth','1b) EBIT Growth','1c) Bottom Line Growth','2a) Profit Margin','2b) Stability of Profit Margin'\
        ,'2c) Sign of Operating CF','3a) ROE','3b) CROE','3c) Stability of Returns', '3d) Sign of FCF', '3e) Cash Reinvestment Rate','4a) Net Debt to Operating CF','4b) Net Debt to Equity'])
    score_df['Weights'] = [5,10,10,10,5,1000,7,13,3,1000,7,10,10]
    
    
    
    # Part 1: Sales performance
    ## 1a) Top Line Growth
    summary_df.loc['Turnover Growth (%)'] = database.loc['Total Turnover'].pct_change() * 100
    value = weighted_average(summary_df.loc['Turnover Growth (%)'])
    score = value_to_score(value,{-999:-3,-5:-1,0:0,10:1,20:1.5,30:2.5,40:3.75,50:4.5,60:5})

    score_df['Reference Value'][0] = value
    score_df['Score'][0] = score


    ## 1b) EBIT Growth
    summary_df.loc['Operating Profit Growth (%)'] = database.loc['Operating Profit'].pct_change() * 100
    value = weighted_average(summary_df.loc['Operating Profit Growth (%)'])
    score = value_to_score(value,{-999:-3,0:0,10:1,20:1.5,30:2.5,40:3.75,50:4.5,60:5})

    score_df['Reference Value'][1] = value
    score_df['Score'][1] = score


    ## 1c) Bottom Line Growth
    summary_df.loc['Net Profit Growth (%)'] = database.loc['Net Profit Growth (%)']
    value = weighted_average(summary_df.loc['Operating Profit Growth (%)'])
    score = value_to_score(value,{-999:-3,0:0,5:1,10:2,20:3,30:4,40:5})

    score_df['Reference Value'][2] = value
    score_df['Score'][2] = score




    # Part 2: Earnings Quality
    ## 2a) Profit Margin
    summary_df.loc['Net Profit Margin (%)'] = database.loc['Net Profit Margin (%)']
    value = weighted_average(summary_df.loc['Net Profit Margin (%)'])
    score = value_to_score(value,{-999:-3,0:0,6:1,10:1.5,13:2.5,17:3.75,19:4.5,22:5})

    score_df['Reference Value'][3] = value
    score_df['Score'][3] = score


    ## 2b) Stability of Profit Margin
    summary_df.loc['Net Profit Margin (%)'] = database.loc['Net Profit Margin (%)']
    value = standard_deviation(summary_df.loc['Net Profit Margin (%)'])
    score = 5/3 if value < 5 else 0

    score_df['Reference Value'][4] = value
    score_df['Score'][4] = score


    ## 2c) Sign of Operating CF
    summary_df.loc['Net Cash Flow from Operating Activities'] = database.loc['Net Cash Flow from Operating Activities'] + database.loc['Taxes (Paid) / Refunded']
    value = -1 if (summary_df.loc['Net Cash Flow from Operating Activities'][-2:].astype(float) < 0).any() == True else 1
    score = -999 if value == -1 else 0

    score_df['Reference Value'][5] = value
    score_df['Score'][5] = score




    # Part 3: Profitability
    ## 3a) ROE
    summary_df.loc['Return on Equity (%)'] = database.loc['Return on Equity (%)']
    value = weighted_average(summary_df.loc['Return on Equity (%)'])
    score = value_to_score(value,{-999:-3,0:1,12:2,18:3,21:4,24:5})

    score_df['Reference Value'][6] = value
    score_df['Score'][6] = score


    ## 3b) CROE
    summary_df.loc['Cash Return on Equity (%)'] = (database.loc['Net Cash Flow from Operating Activities'] + database.loc['Taxes (Paid) / Refunded']) / database.loc['Total Equity'] * 100
    value = weighted_average(summary_df.loc['Cash Return on Equity (%)'])
    score = value_to_score(value,{-999:-3,0:1,12:2,18:3,21:4,24:5})

    score_df['Reference Value'][7] = value
    score_df['Score'][7] = score


    ## 3c) Stability of Returns
    summary_df.loc['Stability of Returns'] = database.loc['Net Profit Margin (%)']
    value = (standard_deviation(summary_df.loc['Return on Equity (%)']) + standard_deviation(summary_df.loc['Cash Return on Equity (%)'])) / 2
    score = 5/3 if value < 5 else 0

    score_df['Reference Value'][8] = value
    score_df['Score'][8] = score


    ## 3d) Sign of FCF
    summary_df.loc['FCF'] = (database.loc['Net Cash Flow from Operating Activities'] + database.loc['Taxes (Paid) / Refunded']) - database.loc['Net Cash Flow from Investing Activities']
    value = -1 if (summary_df.loc['FCF'][-2:].astype(float) < 0).any() == True else 1
    score = -999 if value == -1 else 0

    score_df['Reference Value'][9] = value
    score_df['Score'][9] = score

    ## 3e) Cash Reinvestment Rate
    summary_df.loc['Cash Reinvestment Rate'] = -database.loc['Net Cash Flow from Investing Activities'] / (database.loc['Net Cash Flow from Operating Activities'] - database.loc['Taxes (Paid) / Refunded']) * 100
    value = weighted_average(summary_df.loc['Cash Reinvestment Rate'])
    score = value_to_score(value,{-999:5,0:4,15:3,30:2,45:1,60:0})

    score_df['Reference Value'][10] = value
    score_df['Score'][10] = score


    # Part 4: Solvency
    ## 4a) Net Debt to Operating CF
    summary_df.loc['Net Debt'] = database.loc['Total Debt'] - database.loc['Cash & Cash Equivalents at End of Year']
    summary_df.loc['Net Debt to Operating CF'] = summary_df.loc['Net Debt'] / database.loc['Net Cash Flow from Operating Activities']
    value = weighted_average(summary_df.loc['Net Debt to Operating CF'])
    score = value_to_score(value,{-999:5,0:4,3:3,4:2,6:1,8:0})

    score_df['Reference Value'][11] = value
    score_df['Score'][11] = score

    ## 4b) Net Debt to Equity
    summary_df.loc['Net Debt to Equity'] = summary_df.loc['Net Debt'] / database.loc['Total Equity']
    value = weighted_average(summary_df.loc['Net Debt to Equity'])
    score = value_to_score(value,{-999:5,0:4,15:3,30:2,45:1,55:0})

    score_df['Reference Value'][12] = value
    score_df['Score'][12] = score




    # Part 5: Calculate scores
    score_df['Weighted Score'] = score_df['Score'] / 5 * score_df['Weights']
    score = score_df['Weighted Score'].sum()
    
    return summary_df, score_df, score


def main():
    ticker = ' '
    ticker = input('Please Input the Ticker: ')
    while ticker != '':
        summary_df,score_df,score = score_calculation(ticker)

        print(summary_df)
        print('-------')
        print(score_df)
        print('-------')
        print('Total Score of ' + company_name(ticker) + ': ' + str("{:.2f}".format(score)))
        print('-------')
        
        ticker = input('Please Input the Ticker: ')


if __name__ == "__main__":
    main()