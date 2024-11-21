import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import mplfinance as mpf

def load_and_inspect_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Date'])
    print("First 10 rows of the dataset:")
    print(df.head(10))
    missing_data = df.isnull().sum()
    print("\nMissing data in each column:")
    print(missing_data)
    df.fillna(method='ffill', inplace=True)
    return df

def plot_closing_price(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df['Date'], df['Close'], label='Close Price')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.title('Closing Price over Time')
    plt.legend()
    plt.show()

def plot_candlestick_chart(df):
    df_mpf = df.set_index('Date')
    mpf.plot(df_mpf, type='candle', volume=True, style='yahoo', title='Candlestick Chart')

def daily_return_analysis(df):
    df['Daily Return'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    avg_daily_return = df['Daily Return'].mean()
    median_daily_return = df['Daily Return'].median()
    std_closing_price = df['Close'].std()
    print(f"Average Daily Return: {avg_daily_return:.2f}%")
    print(f"Median Daily Return: {median_daily_return:.2f}%")
    print(f"Standard Deviation of Closing Price: {std_closing_price:.2f}")
    return df

def plot_moving_averages(df):
    df['50_MA'] = df['Close'].rolling(window=50).mean()
    df['200_MA'] = df['Close'].rolling(window=200).mean()
    plt.figure(figsize=(10, 5))
    plt.plot(df['Date'], df['Close'], label='Close Price')
    plt.plot(df['Date'], df['50_MA'], label='50-Day MA', color='orange')
    plt.plot(df['Date'], df['200_MA'], label='200-Day MA', color='green')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Moving Averages (50-Day and 200-Day)')
    plt.legend()
    plt.show()

def plot_volatility(df):
    df['30_Rolling_Std'] = df['Close'].rolling(window=30).std()
    plt.figure(figsize=(10, 5))
    plt.plot(df['Date'], df['30_Rolling_Std'], label='30-Day Rolling Std (Volatility)', color='red')
    plt.xlabel('Date')
    plt.ylabel('Volatility')
    plt.title('30-Day Rolling Volatility')
    plt.legend()
    plt.show()

def identify_trends(df):
    df['Trend'] = np.where(df['50_MA'] > df['200_MA'], 'Bullish', 'Bearish')
    plt.figure(figsize=(10, 5))
    plt.plot(df['Date'], df['Close'], label='Close Price')
    plt.plot(df['Date'], df['50_MA'], label='50-Day MA', color='orange')
    plt.plot(df['Date'], df['200_MA'], label='200-Day MA', color='green')
    bullish = df[df['Trend'] == 'Bullish']
    bearish = df[df['Trend'] == 'Bearish']
    plt.scatter(bullish['Date'], bullish['Close'], color='green', label='Bullish', marker='^', alpha=1)
    plt.scatter(bearish['Date'], bearish['Close'], color='red', label='Bearish', marker='v', alpha=1)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Bullish and Bearish Trends')
    plt.legend()
    plt.show()
file_path = 'C:\\study\\stock\\infy_stock.csv'
df = load_and_inspect_data(file_path)
plot_closing_price(df)
plot_candlestick_chart(df)
df = daily_return_analysis(df)
plot_moving_averages(df)
plot_volatility(df)
identify_trends(df)