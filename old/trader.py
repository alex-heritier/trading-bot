import time
import threading

import util
import test_strategy
import rh_broker as broker
import db

WAIT_TIME = 2 # seconds

t_trader = None
t_trader_running = False

### Lifecycle methods
def start():
    global t_trader, t_trader_running
    util.log("START", key='trader')
    t_trader_running = True
    t_trader = threading.Thread(target=run_main_loop, daemon=True)
    t_trader.start()
    return t_trader

def stop():
    global t_trader_running
    util.log("STOP", key='trader')
    t_trader_running = False

### Trade actions
def run_main_loop():
    # Initialize
    broker.init()
    db.reset_db()

    # Begin main loop of polling current price data then acting on it
    while t_trader_running:
        test_strategy.tick_action()
        time.sleep(WAIT_TIME)
