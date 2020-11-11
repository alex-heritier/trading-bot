import robin_stocks as r
from decimal import *
import yaml
import time

import util
import rh_broker as broker
import db

CREDENTIALS_FILENAME = 'robinhood_credentials.yml'

CRYPTO_SYMBOLS = ['DOGE', 'ETC', 'LTC']
WAIT_TIME = 2 # seconds

price_history = {}

### Helper Methods
def login():
    with open(CREDENTIALS_FILENAME, 'r') as stream:
        data = yaml.safe_load(stream)
    r.login(data['email'], data['password'])

def tick_action():
    for symbol in CRYPTO_SYMBOLS:
        run_crypto_algo(symbol)

def run_crypto_algo(symbol):
    curr_price = broker.get_crypto_price(symbol)
    if symbol not in price_history:
        price_history[symbol] = curr_price
    last_price = price_history[symbol]

    if symbol == 'ETC':
        amount = 2
    elif symbol == 'DOGE':
        amount = 10000
    elif symbol == 'LTC':
        amount = 0.5
    elif symbol == 'BTC':
        amount = 0.002
    amount *= 3 # multiplier

    sell_to_buy_ratio = 1.15

    if Decimal(curr_price) < Decimal(last_price):
        broker.buy_crypto(symbol, amount)
    elif Decimal(curr_price) > Decimal(last_price):
        broker.sell_crypto(symbol, util.safe_mult(amount, sell_to_buy_ratio))
    else:
        util.log("no trade for %s..."%symbol)

    price_history[symbol] = curr_price

### Program Start
# Login to Robinhood using credentials file
l = login()

### Begin main loop of polling current price data then acting on it
db.reset_db()
while True:
    tick_action()
    time.sleep(WAIT_TIME)
