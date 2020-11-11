import json
from decimal import *
from threading import Thread, Lock
import traceback
import functools

import util

DB_FILENAME = "db.json"

_file_mutex = Lock()

### Database manipulation
def _open_db():
    with open(DB_FILENAME, 'r') as stream:
        data = json.load(stream)
    return data

def _save_db(db):
    with open(DB_FILENAME, 'w') as stream:
        json.dump(db, stream, indent=2)

class _Db:
    def read(self):
        return _open_db()

    def write(self, db):
        return _save_db(db)

class _DbContext(object):
    db = None
    def __init__(self):
        _file_mutex.acquire()
        self.db = _Db()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value != None:
            print('An error occurred %s: %s' % (self.db, exc_value))
            traceback.print_tb(exc_traceback)
        _file_mutex.release()
        return True

def reset_db():
    with _DbContext() as ctx:
        db = ctx.read()
        db = {}
        db['total'] = '1000'
        db['cash'] = db['total']
        db['equity'] = '0'
        db['original_capital'] = db['total']
        db['growth'] = '0'
        db['positions'] = {'id_counter': 0, 'crypto': []}
        db['transactions'] = {'id_counter': 0, 'crypto': []}
        ctx.write(db)

### Balance
def get_cash_balance():
    with _DbContext() as ctx:
        db = ctx.read()
    return Decimal(db['cash'])

def modify_cash_balance(delta):
    with _DbContext() as ctx:
        db = ctx.read()
        db['cash'] = str(Decimal(db['cash']) + Decimal(delta))
        db['total'] = str(Decimal(db['total']) + Decimal(delta))
        return ctx.write(db)

def get_equity_balance():
    with _DbContext() as ctx:
        db = ctx.read()
    return Decimal(db['equity'])

def update_equity_balance():
    with _DbContext() as ctx:
        db = ctx.read()
        balance = functools.reduce(lambda sum, p : util.safe_num(Decimal(sum) + Decimal(p['total_price'])), db['positions']['crypto'], 0)
        db['equity'] = str(Decimal(balance))
        db['total'] = str(util.safe_num(Decimal(db['cash']) + Decimal(db['equity'])))
        db['growth'] = str(util.safe_mult(util.safe_div(db['total'], db['original_capital']) - 1, 100))
        return ctx.write(db)

### Positions
## Crypto
def get_crypto_positions_by_symbol(symbol):
    with _DbContext() as ctx:
        db = ctx.read()
    crypto = db['positions']['crypto']
    return list(filter(lambda p : p['symbol'] == symbol, crypto))

def add_crypto_position(symbol, price, quantity):
    with _DbContext() as ctx:
        db = ctx.read()
        id = db['positions']['id_counter']
        db['positions']['id_counter'] += 1
        timestamp = util.current_timestamp()
        data = {
            "id": id,
            "symbol": symbol,
            "timestamp": timestamp,
            "unit_price": str(Decimal(price)),
            "total_price": str(util.safe_mult(price, quantity)),
            "quantity": str(Decimal(quantity)),
        }
        db['positions']['crypto'].append(data)
        ctx.write(db)
        return data

def remove_crypto_positions(symbol, quantity):
    with _DbContext() as ctx:
        db = ctx.read()
        rm_pos = []
        for pos in db['positions']['crypto']:
            if pos['symbol'] == symbol:
                if Decimal(pos['quantity']) <= Decimal(quantity): # Empty position
                    rm_pos.append(pos['id'])
                    quantity = util.safe_num(Decimal(quantity) - Decimal(pos['quantity']))
                else:                                            # Reduce position size
                    old_position_quantity = pos['quantity']
                    pos['quantity'] = str(util.safe_num(Decimal(pos['quantity']) - Decimal(quantity)))
                    pos['total_price'] = str(util.safe_mult(pos['quantity'], pos['unit_price']))
                    quantity = util.safe_num(Decimal(quantity) - Decimal(old_position_quantity))
                if quantity <= 0:
                    break
        db['positions']['crypto'] = list(filter(lambda p : p['id'] not in rm_pos, db['positions']['crypto']))
        ctx.write(db)

### Transactions
## Crypto
def add_crypto_transaction(symbol, price, quantity, side):
    with _DbContext() as ctx:
        db = ctx.read()
        id = db['transactions']['id_counter']
        db['transactions']['id_counter'] += 1
        timestamp = util.current_timestamp()
        data = {
            "id": id,
            "symbol": symbol,
            "timestamp": timestamp,
            "unit_price": str(Decimal(price)),
            "total_price": str(util.safe_mult(price, quantity)),
            "quantity": str(Decimal(quantity)),
            "side": side,
        }
        db['transactions']['crypto'].append(data)
        ctx.write(db)
        return data
