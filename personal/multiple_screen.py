import os
os.chdir('/Users/tinglam/Documents/GitHub/value_investing')
import screening

# Cement
stock_list = [1313,914,2128,3323,1252,743,691,2233,726,2009,2060,695,366,1312,9913]
my_dict = {}

for ticker in stock_list:
    summary_df,score_df,score = screening.score_calculation(ticker)
    my_dict[ticker] = score

{k: v for k, v in sorted(my_dict.items(), key=lambda item: item[1])}