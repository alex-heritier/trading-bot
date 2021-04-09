import json
from decimal import *
from threading import Thread, Lock
import traceback
import functools

import util

DB_DIRECTORY = "db"

ACCOUNTING_DB = "acc" # Account balances
POSITIONS_DB = "pos" # Positions
TRANSACTIONS_DB = "tx" # Transactions

DB_LIST = [ACCOUNTING_DB, POSITIONS_DB, TRANSACTIONS_DB]

_file_mutex = Lock()

### Database manipulation
def _full_db_path(db_name):
    return DB_DIRECTORY + '/' + db_name + '.json'

def _open_db(db_name):
    with open(_full_db_path(db_name), 'r') as stream:
        return json.load(stream)

def _save_db(db_name, data):
    with open(_full_db_path(db_name), 'w') as stream:
        json.dump(data, stream, indent=2)

class _DbCollection:
    def account(self):
        return _Db(ACCOUNTING_DB)

    def positions(self):
        return _Db(POSITIONS_DB)

    def transactions(self):
        return _Db(TRANSACTIONS_DB)

class _Db:
    def __init__(self, db_filename):
        self.filename = db_filename

    def read(self):
        return _open_db(self.filename)

    def write(self, db):
        return _save_db(self.filename, db)

class _DbContext(object):
    def __init__(self):
        _file_mutex.acquire()
        self.db_collection = _DbCollection()

    def __enter__(self):
        return self.db_collection

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value != None:
            print('An error occurred %s: %s' % (self.db_collection, exc_value))
            traceback.print_tb(exc_traceback)
        _file_mutex.release()
        return True

def reset_db():
    with _DbContext() as ctx:
        initial_amt = '1000'
        ctx.account().write({
            'total': initial_amt,
            'cash': initial_amt,
            'equity': '0',
        })

        ctx.positions().write({
            'id_counter': 0,
            'crypto': [],
        })

        ctx.transactions().write({
            'id_counter': 0,
            'crypto': [],
        })


### Balance
def get_cash_balance():
    with _DbContext() as ctx:
        db = ctx.account().read()
    return Decimal(db['cash'])

def modify_cash_balance(delta):
    with _DbContext() as ctx:
        db = ctx.account().read()
        db['cash'] = str(Decimal(db['cash']) + Decimal(delta))
        db['total'] = str(Decimal(db['total']) + Decimal(delta))
        return ctx.account().write(db)

def get_equity_balance():
    with _DbContext() as ctx:
        db = ctx.account().read()
    return Decimal(db['equity'])

def update_equity_balance():
    with _DbContext() as ctx:
        acc_db = ctx.account().read()
        pos_db = ctx.positions().read()
        balance = functools.reduce(lambda sum, p : util.safe_num(Decimal(sum) + Decimal(p['total_price'])), pos_db['crypto'], 0)
        acc_db['equity'] = str(Decimal(balance))
        acc_db['total'] = str(util.safe_num(Decimal(acc_db['cash']) + Decimal(acc_db['equity'])))
        ctx.positions().write(pos_db)
        return ctx.account().write(acc_db)

### Positions
## Crypto
def get_crypto_positions_by_symbol(symbol):
    with _DbContext() as ctx:
        db = ctx.positions().read()
    crypto = db['crypto']
    return list(filter(lambda p : p['symbol'] == symbol, crypto))

def add_crypto_position(symbol, price, quantity):
    with _DbContext() as ctx:
        pos_db = ctx.positions().read()
        id = pos_db['id_counter']
        pos_db['id_counter'] += 1
        timestamp = util.current_timestamp()
        data = {
            "id": id,
            "symbol": symbol,
            "timestamp": timestamp,
            "unit_price": str(Decimal(price)),
            "total_price": str(util.safe_mult(price, quantity)),
            "quantity": str(Decimal(quantity)),
        }
        pos_db['crypto'].append(data)
        ctx.positions().write(pos_db)
        return data

def remove_crypto_positions(symbol, quantity):
    with _DbContext() as ctx:
        pos_db = ctx.positions().read()
        rm_pos = []
        for pos in pos_db['crypto']:
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
        pos_db['crypto'] = list(filter(lambda p : p['id'] not in rm_pos, pos_db['crypto']))
        ctx.positions().write(pos_db)

### Transactions
## Crypto
def add_crypto_transaction(symbol, price, quantity, side):
    with _DbContext() as ctx:
        db = ctx.transactions().read()
        id = db['id_counter']
        db['id_counter'] += 1
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
        db['crypto'].append(data)
        ctx.transactions().write(db)
        return data
