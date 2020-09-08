import os
os.chdir('/Users/tinglam/Documents/GitHub/value_investing')
import statements_scraper
import pandas as pd
import openpyxl


ticker = '743'

df = statements_scraper.scrape_statements(ticker)


with pd.ExcelWriter('screening.xlsx',engine="openpyxl", mode="a") as writer:  
    df.to_excel(writer, sheet_name=ticker)
    writer.save()
    writer.close()