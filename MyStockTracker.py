import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

st.set_page_config(
    page_title='MyStockTracker',
    page_icon='book'
)  

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("MyStockTracker 📈")
st.write("Select which stock you want to research, and navigate through each page to receive analysis")
 

def get_stock_data(symbol, api_key, interval='5min'):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def get_stock_overview(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def graphs(symbol):
    st.subheader("""Daily **closing price** for """ + symbol)
    #get data on searched ticker
    stock_data = yf.Ticker(symbol)
    #get historical data for searched ticker
    stock_df = stock_data.history(period='1d', start='2020-01-01', end=None)
    #print line chart with daily closing prices for searched ticker
    st.line_chart(stock_df.Close)

    #define variable today 
    today = datetime.today().strftime('%Y-%m-%d')
    #get current date data for searched ticker
    stock_lastprice = stock_data.history(period='1d', start=today, end=today)

    #stock actions
    st.subheader("""Stock **actions** for """ + symbol)
    display_action = (stock_data.actions)
    if display_action.empty == True:
        st.write("No data available at the moment")
    else:
        st.write(display_action)

    #shareholders
    st.subheader("""**Institutional investors** for """ + symbol)
    display_shareholders = (stock_data.institutional_holders)
    if display_shareholders.empty == True:
        st.write("No data available at the moment")
    else:
        st.write(display_shareholders)

def get_stock_performance(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def get_stock_fundamentals(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={api_key}'
    r = requests.get(url)
    data1 = r.json()
    url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={api_key}'
    r = requests.get(url)
    data2 = r.json()
    url = 'https://www.alphavantage.co/query?function=CASH_FLOW&symbol=IBM&apikey=demo'
    r = requests.get(url)
    data3 = r.json()
    return [data1, data2, data3]

# Create a sidebar menu with three options
menu = ["Stock Overview", "Financial Analysis", "My Feed"]
tickerSymbol = st.text_input('What Stock Symbol are you looking for?')
choice = st.selectbox("Select a page", menu)

if choice == "Stock Overview":
    if tickerSymbol == "":
        st.error("Please select a stock to start analysis!")
        st.stop()
    st.title("🕮 Stock Overview")
    
    data = get_stock_overview(tickerSymbol, 'CP8UGW4IQVRGR9V6')
    # Display overview data
    st.subheader(f'{data["Name"]} ({data["Symbol"]})')
    st.write(f'Sector: {data["Sector"]}')
    st.write(f'Industry: {data["Industry"]}')
    st.write(f'Exchange: {data["Exchange"]}')
    st.write(f'Description: {data["Description"]}')
    st.session_state["pe"] = data["PERatio"]
    #Graphs
    graphs(tickerSymbol)

if choice == "Financial Analysis":
    st.title("💵 Financial Analysis")

    stock_data = yf.Ticker(tickerSymbol)
    stock_df = stock_data.history(period='1d', start='2020-01-01', end=None)
    #get daily volume for searched ticker
    st.subheader("""Daily **volume** for """ + tickerSymbol)
    st.line_chart(stock_df.Volume)

    if tickerSymbol == "":
        st.error("Please select a stock to start analysis!")
        st.stop()
    st.subheader("Stock Performance")
    data = get_stock_performance(tickerSymbol, 'CP8UGW4IQVRGR9V6')
    global_quote = data["Global Quote"]
    table_data = [        ["Symbol", global_quote["01. symbol"]],
        ["Open", global_quote["02. open"]],
        ["High", global_quote["03. high"]],
        ["Low", global_quote["04. low"]],
        ["Price", global_quote["05. price"]],
        ["Volume", global_quote["06. volume"]],
        ["Latest Trading Day", global_quote["07. latest trading day"]],
        ["Previous Close", global_quote["08. previous close"]],
        ["PE Ratio", st.session_state["pe"]],
        ["Change Percent", global_quote["10. change percent"]]
    ]
    df = pd.DataFrame(table_data, columns=["Metric", "Value"]).set_index("Metric")
    st.table(df)

    st.subheader("Stock Fundamentals")
    data = get_stock_fundamentals(tickerSymbol, 'CP8UGW4IQVRGR9V6')
    table1= (data[0]["annualReports"][0])
    table2 = (data[1]["annualReports"][0])
    table3 = (data[2]["annualReports"][0])
    table_data = [        ["fiscalDateEnding", table3["fiscalDateEnding"]],
            ["Reported Currency", table3["reportedCurrency"]],
            ["Gross Profit", str(format(int(table1["grossProfit"]), ","))],
            ["Total Revenue", str(format(int(table1["totalRevenue"]), ","))],
            ["Income Before Tax", str(format(int(table1["incomeBeforeTax"]), ","))],
            ["Income Tax Expense", str(format(int(table1["incomeTaxExpense"]), ","))],
            ["Net Income", str(format(int(table1["netIncome"]), ","))],
            ["Total Assets", str(format(int(table2["totalAssets"]), ","))],
            ["Ineventory", str(format(int(table2["inventory"]), ","))],
            ["Investments", str(format(int(table2["investments"]), ","))],
            ["Current Debt", str(format(int(table2["currentDebt"]), ","))],
            ["Operating Cash Flow", str(format(int(table3["operatingCashflow"]), ","))]
        ]
    df = pd.DataFrame(table_data, columns=["Metric", "Value"]).set_index("Metric")
    st.table(df)
if choice == "My Feed":
    st.title("📰 Your Feed")
    st.markdown("A tailored feed of articles about recent market changes updates.")
    st.markdown("---")
    url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo'
    r = requests.get(url)
    for i in range(50):
        data = r.json()["feed"][i]

        # Display article information
        st.markdown(f"### {data['title']}")
        st.markdown(f"**Published:** {data['time_published']}")
        st.markdown(f"**Authors:** {', '.join(data['authors'])}")
        st.markdown(f"**Source:** {data['source']}")
        st.markdown(f"**Summary:** {data['summary']}")
        st.markdown(f"**Link:** {data['url']}")
        st.image(data['banner_image'], use_column_width=True)

        st.markdown("---")