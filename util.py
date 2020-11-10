import datetime
from decimal import *


def date_to_str(date):
    return date.strftime('%m/%d/%y %H:%M:%S.%f')[:-3]

def current_timestamp():
    return date_to_str(datetime.datetime.now())

def log(z):
    print(current_timestamp() + " - " + z)

def safe_num(a):
    return round(Decimal(a), 6)

def safe_mult(a, b):
    return safe_num(Decimal(a) * Decimal(b))
