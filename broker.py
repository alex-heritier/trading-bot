import robin_stocks as r
from decimal import *
import functools

import util
import db

BUY_SIDE = 'buy'
SELL_SIDE = 'sell'

# Crypto
def get_crypto_price(symbol):
    price_data = r.get_crypto_quote(symbol)
    return Decimal(price_data['mark_price'])

def buy_crypto(symbol, amount):
    amount = util.safe_num(amount)
    price = get_crypto_price(symbol)
    total = util.safe_mult(price, amount)

    # Check balance
    current_balance = db.get_cash_balance()
    if total > current_balance:
        util.log("! trying to buy %s %s but only have $%s in balance" % (amount, symbol, current_balance))
        return False

    db.modify_cash_balance(-total)
    db.add_crypto_position(symbol=symbol, price=price, quantity=amount)
    db.add_crypto_transaction(symbol=symbol, price=price, quantity=amount, side=BUY_SIDE)
    db.update_equity_balance()
    util.log("[BOUGHT] %s x %s @ $%s for $%s" % (symbol, amount, price, total))
    return True

def sell_crypto(symbol, amount):
    amount = util.safe_num(amount)
    price = get_crypto_price(symbol)
    total = util.safe_mult(price, amount)

    # Check positions
    positions = db.get_crypto_positions_by_symbol(symbol)
    qty_of_symbol = functools.reduce(lambda sum, p : sum + Decimal(p['quantity']), positions, 0)
    if amount > qty_of_symbol:
        util.log("! trying to sell %s %s but only own %s"%(symbol, amount, qty_of_symbol))
        return False

    db.modify_cash_balance(total)
    db.remove_crypto_positions(symbol=symbol, quantity=amount)
    db.add_crypto_transaction(symbol=symbol, price=price, quantity=amount, side=SELL_SIDE)
    db.update_equity_balance()
    util.log("[SOLD] %s x %s @ $%s for $%s" % (amount, symbol, price, total))
    return True
