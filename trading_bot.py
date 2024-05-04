import pandas as pd
from classify_tickers import get_sectors_or_update_sectors
import yfinance as yf

# Load the dataset
df = pd.read_csv(get_sectors_or_update_sectors())

# Define sectors that perform well and poorly in recessions
good_sectors = ["Utilities", "Consumer Goods"]
bad_sectors = ["Technology", "Industrial Goods"]


# Go long on good sectors
def long():
    for ticker in df[df["Sector"].isin(good_sectors)]["Ticker"]:
        print(f"Going long on: {ticker}")
    # Here you would use your trading platform's API to buy the stock
    # For example, if you were using Alpaca:
    # api.submit_order(
    #     symbol=ticker,
    #     qty=1,
    #     side='buy',
    #     type='market',
    #     time_in_force='gtc'
    # )


# Short stocks in bad sectors
def short():
    for ticker in df[df["Sector"].isin(bad_sectors)]["Ticker"]:
        print(f"Shorting: {ticker}")
    # Here you would use your trading platform's API to short the stock
    # For example, if you were using Alpaca:
    # api.submit_order(
    #     symbol=ticker,
    #     qty=1,
    #     side='sell',
    #     type='market',
    #     time_in_force='gtc'
    # )


def main():
    long()
    short()


if __name__ == "__main__":
    main()
