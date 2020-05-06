import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from bs4 import BeautifulSoup
#from value_investing.fin_scraping import *
from fin_scraping import all_pages_scraped
import requests
import pandas as pd


def generate_table(dataframe, max_rows=100):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    dcc.Input(id = 'input'),

    #html.H2()

    html.H3(id = 'stock-name'),
    html.H3(id = 'stock-price'),
    html.Table(id='fin-table'),


])

# Table
@app.callback(
    Output(component_id='fin-table', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_table(input_value):
    df = all_pages_scraped(input_value)
    return generate_table(df)

# Name
@app.callback(
    Output(component_id='stock-name', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_name(input_value):
    yahoo_url = r"https://finance.yahoo.com/quote/" + input_value + ".HK"
    name = BeautifulSoup(requests.get(yahoo_url).text,'lxml').find("h1").text
    return name

# Price
@app.callback(
    Output(component_id='stock-price', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_price(input_value):
    yahoo_url = r"https://finance.yahoo.com/quote/" + input_value + ".HK"
    price = BeautifulSoup(requests.get(yahoo_url).text,'lxml').findAll('div')[3].findAll('div')[0].findAll('div')[0].findAll('span')[13].text
    return "Current Price: " + price


if __name__ == '__main__':
    app.run_server(debug=True)
