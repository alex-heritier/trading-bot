import logging
import datetime
from decimal import *

logger = None

def date_to_str(date):
    return date.strftime('%m/%d/%y %H:%M:%S.%f')[:-3]

def current_timestamp():
    return date_to_str(datetime.datetime.now())

def log(z, key='default'):
    global logger
    if logger == None:
        logger = logging.getLogger('trading-bot-default')
        hdlr = logging.FileHandler('log/' + key + '.log')
        formatter = logging.Formatter('%(asctime)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.WARNING)
    logger.warning(z)

def safe_num(a):
    return round(Decimal(a), 6)

def safe_mult(a, b):
    return safe_num(Decimal(a) * Decimal(b))

def safe_div(a, b):
    return safe_num(Decimal(a) / Decimal(b))
