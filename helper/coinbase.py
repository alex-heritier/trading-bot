import requests

# Historic Rates - example URL for getting historical price data
# - https://api.pro.coinbase.com/products/btc-usd/candles?start=01-01-2021&end=01-02-2021&granularity=300

def get_ticker_price(ticker_pair):
    r = requests.get("https://api.coinbase.com/v2/prices/%s/spot"%ticker_pair)
    return r

def get_historical_rates(ticker_pair):
    r = requests.get("https://api.pro.coinbase.com/products/%s/candles?start=01-01-2021&end=01-02-2021&granularity=300"%ticker_pair)
    return r
