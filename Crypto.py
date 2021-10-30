import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
import time

#New feature(make sure to upgrade streamlit library)

#Page Layout
##Page expands to full width
st.set_page_config(layout = "wide")

#Title
image = Image.open('logo.jpg')

st.image(image, width =500)

st.title('Crypto Price App')
st.markdown("""
This app retrieves Cryptocurrency Prices for the top 100 Cryptocurrency from the **CoinMarketCap**!
""")

# About
expander_bar = st.beta_expander("About")
expander_bar.markdown("""
* **Python libraries"** base64, streamlit, matplotlib.pyplot,BeautifulSoup, requests, json, time
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).
* **Credit:** Web scraper adapted from the Medium article *[Web Scraping Crypto Prices With Python](https://towardsdatascience.com/web-scraping-crypto-prices-with-python-41072ea5b5bf)* written by [Bryan Feng](https://medium.com/@bryanf).
""")

#Page Layout(continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 =  st.beta_columns((2,1))


#sidebar + main panel
col1.header('Input Options')

#sidebar - Currency Price unit
currency_price_unit = col1.selectbox('Select Currency for Price',('USD', 'BTC', 'ETH'))

#Webscraping of CoinMarketCap data
@st.cache
def load_data():
    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')


    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listing = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][1:]
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    
    for i in listing:
      coins[str(i[8])] = i[125]

    price = []
    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []
    #x = 'abc'+currency_price_unit
    for i in listing:
        coin_name.append(i[125])
        coin_symbol.append(i[126])
        if(currency_price_unit == 'USD'):
            price.append(i[64])
            percent_change_1h.append(i[58])
            percent_change_24h.append(i[59])
            percent_change_7d.append(i[62])
            market_cap.append(i[55])
            volume_24h.append(i[66])
        elif (currency_price_unit == 'BTC'):
            price.append(i[28])
            percent_change_1h.append(i[22])
            percent_change_24h.append(i[23])
            percent_change_7d.append(i[26])
            market_cap.append(i[19])
            volume_24h.append(i[30])
        
        else:
            price.append(i[46])
            percent_change_1h.append(i[40])
            percent_change_24h.append(i[41])
            percent_change_7d.append(i[44])
            market_cap.append(i[37])
            volume_24h.append(i[48])
        

    df = pd.DataFrame(columns = ['coin_name', 'coin_symbol', 'market_cap', 'percent_change_1h', 'percent_change_24h','percent_change_7d', 'price', 'volume_24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percent_change_1h'] = percent_change_1h
    df['percent_change_24h'] =  percent_change_24h
    df['percent_change_7d'] = percent_change_7d
    df['market_cap'] = market_cap
    df['volume_24h'] = volume_24h
    return df


df = load_data()

##Sidebar - Cryptocurrency selections

sorted_coin = sorted(df['coin_symbol'])
selected_coin =  col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

df_selected_coin = df[ (df['coin_symbol'].isin(selected_coin))]  #filtering data

##Sidebar - Number of coins to display
num_coin = col1.slider('Display Top N Coins', 1,100,100)
df_coins = df_selected_coin[:num_coin]

##Sidebar - Percent change time frame

percent_timeframe = col1.selectbox('percent change time frame',['7d', '24h', '1h'])

percent_dict = {"7d":'percent_change_7d', "24h":'percent_change_24h', "1h":'percent_change_1h'}
selected_percent_timeframe = percent_dict[percent_timeframe]

#sidebar - Sorting Values
sort_values = col1.selectbox('Sort values?',['Yes', 'No'])

col2.subheader('Price Data of Selected Cryptocurrency')
col2.write('Data Dimension: ' + str(df_selected_coin.shape[0])+ ' rows and ' +str(df_selected_coin.shape[1]) + ' columns.')

col2.dataframe(df_coins)


#download CSV data
## https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806


def filedownload(df):
    csv = df.to_csv(index = False)
    b64 = base64.b64encode(csv.encode()).decode()  #strings <-> bytes
    href = f'<a href="data:files/csv;base64,{b64}" download = "crypto.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)


#Preparing Data for bar plot of % Price Change

col2.subheader('Table of % Price Change')
df_change = pd.concat([df_coins.coin_symbol, df_coins.percent_change_1h, df_coins.percent_change_24h, df_coins.percent_change_7d],axis=1)
df_change = df_change.set_index('coin_symbol')
df_change['positive_percent_change_1h'] = df_change['percent_change_1h']>0
df_change['positive_percent_change_24h'] = df_change['percent_change_24h']>0
df_change['positive_percent_change_7d'] = df_change['percent_change_7d']>0
col2.dataframe(df_change)


#conditional creation of Bar plot(time frame)
col3.subheader('Bar Plot of % Price Change')

if percent_timeframe == '7d':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_7d'])
    col3.write('*7 Days period*')
    plt.figure(figsize = (5,25))
    plt.subplots_adjust(top=1,bottom = 0)
    df_change['percent_change_7d'].plot(kind = 'barh', color =df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)

elif percent_timeframe == '24h':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_24h'])
    col3.write('*24 hour period*')
    plt.figure(figsize = (5,25))
    plt.subplots_adjust(top=1,bottom = 0)
    df_change['percent_change_24h'].plot(kind = 'barh', color =df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
else:
    if sort_values == 'Yes':
        df_changes = df_change.sort_values(by=['percent_change_1h'])
    col3.write('*1 hour period*')
    plt.figure(figsize = (5,25))
    plt.subplots_adjust(top =1, bottom = 0)
    df_change['percent_change_1h'].plot(kind ='barh', color =df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)