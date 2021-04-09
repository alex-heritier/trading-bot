import robin_stocks as r
from decimal import *

import util
import rh_broker as broker

CRYPTO_SYMBOLS = ['DOGE', 'BTC', 'ETH']

price_history = {}

def tick_action():
    for symbol in CRYPTO_SYMBOLS:
        run_crypto_algo(symbol)

def run_crypto_algo(symbol):
    curr_price = broker.get_crypto_price(symbol)
    if symbol not in price_history:
        price_history[symbol] = curr_price
    last_price = price_history[symbol]

    if symbol == 'ETH':
        amount = 0.05
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
        util.log("no trade for %s..."%symbol, key='trader')

    price_history[symbol] = curr_price
