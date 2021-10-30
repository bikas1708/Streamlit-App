import yfinance as yf
import streamlit as st
import pandas as pd


st.write("""
# Simple Stock Price App


Shown are the stock closing price and volume of google!


""")

#define the ticker symbol
tickerSymbol = 'GOOGL'

#get the data on this ticker
tickerData = yf.Ticker(tickerSymbol)

#Get the historical prices for this ticker
tickerDf = tickerData.history(period='1mo', start='2010-1-1', end='2020-1-25')

#Open High   Low Close   Volume  Dividends   Stock Splits


st.write("""
## Closing Price
""")
st.line_chart(tickerDf.Close)
st.write("""
## Volume Price
""")
st.line_chart(tickerDf.Volume)
st.write("""
## Highest Price
""")
st.line_chart(tickerDf.High)
