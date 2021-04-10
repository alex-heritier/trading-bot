import requests

# Historic Rates - example URL for getting historical price data
# - https://api.pro.coinbase.com/products/btc-usd/candles?start=01-01-2021&end=01-02-2021&granularity=300

def get_ticker_price(ticker_pair, type="spot"):
    url = "https://api.coinbase.com/v2/prices/%s/%s"%(ticker_pair, type)
    print("helper.coinbase - %s"%url)
    r = requests.get(url)
    return r

def get_historical_rates(ticker_pair, granularity="300"):
    start = None # "01-01-2021"
    end = None # "01-02-2021"

    url = ("https://api.pro.coinbase.com/products/%s/candles?"%ticker_pair)
    if start:
        url = ("%s&start=%s"%(url, start))
    if end:
        url = ("%s&end=%s"%(url, end))
    if granularity:
        url = ("%s&granularity=%s"%(url, granularity))

    print("helper.coinbase - %s"%url)
    r = requests.get(url)
    return r
