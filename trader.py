import robin_stocks as r
from decimal import *
import time
import threading

import util
import rh_broker as broker
import db

CRYPTO_SYMBOLS = ['DOGE', 'BTC', 'ETH']
WAIT_TIME = 2 # seconds

price_history = {}
t_trader = None
t_trader_running = False

### Lifecycle methods
def start():
    global t_trader, t_trader_running
    util.log("START", key='trader')
    t_trader_running = True
    t_trader = threading.Thread(target=trade, daemon=True)
    t_trader.start()
    return t_trader

def stop():
    global t_trader_running
    util.log("STOP", key='trader')
    t_trader_running = False

### Trade actions
def trade():
    # Initialize
    broker.init()
    db.reset_db()

    # Begin main loop of polling current price data then acting on it
    while t_trader_running:
        tick_action()
        time.sleep(WAIT_TIME)

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
