import robin_stocks as r
from threading import Thread, Lock
from decimal import *
import functools
import yaml

import util
import db

CREDENTIALS_FILENAME = 'robinhood_credentials.yml'

BUY_SIDE = 'buy'
SELL_SIDE = 'sell'

_broker_mutex = Lock()

### General
def init():
    try:
        with open(CREDENTIALS_FILENAME, 'r') as stream:
            data = yaml.safe_load(stream)
            email = data['email']
            password = data['password']
    except:
        print("Credentials file missing! Defaulting to manual input.")
        email = input("Your email: ")
        password = input("Your password: ")
    r.login(email, password)


### Crypto
def get_crypto_price(symbol):
    price_data = r.get_crypto_quote(symbol)
    return Decimal(price_data['mark_price'])

def buy_crypto(symbol, amount):
    _broker_mutex.acquire()

    amount = util.safe_num(amount)
    price = get_crypto_price(symbol)
    total = util.safe_mult(price, amount)

    # Check balance
    current_balance = db.get_cash_balance()
    if total > current_balance:
        util.log("! trying to buy %s %s but only have $%s in balance" % (amount, symbol, current_balance))
        _broker_mutex.release()
        return False

    db.modify_cash_balance(-total)
    db.add_crypto_position(symbol=symbol, price=price, quantity=amount)
    db.add_crypto_transaction(symbol=symbol, price=price, quantity=amount, side=BUY_SIDE)
    db.update_equity_balance()

    _broker_mutex.release()

    util.log("[BOUGHT] %s x %s @ $%s for $%s" % (symbol, amount, price, total))
    return True

def sell_crypto(symbol, amount):
    _broker_mutex.acquire()

    price = get_crypto_price(symbol)

    # Check positions
    positions = db.get_crypto_positions_by_symbol(symbol)
    qty_of_symbol = functools.reduce(lambda sum, p : sum + Decimal(p['quantity']), positions, 0)
    if qty_of_symbol == 0:
        util.log("! trying to sell %s x %s but don't own any"%(amount, symbol))
        _broker_mutex.release()
        return False
    else:
        amount = util.safe_num(min(amount, qty_of_symbol))

    total = util.safe_mult(price, amount)
    db.modify_cash_balance(total)
    db.remove_crypto_positions(symbol=symbol, quantity=amount)
    db.add_crypto_transaction(symbol=symbol, price=price, quantity=amount, side=SELL_SIDE)
    db.update_equity_balance()

    _broker_mutex.release()

    util.log("[SOLD] %s x %s @ $%s for $%s" % (amount, symbol, price, total))
    return True
