import sys

import trader

def cmd_start(_):
    print("Starting trader daemon... (view output in log/trader.log)")
    trader.start()

def cmd_stop(_):
    print("Stopping trader daemon...")
    trader.stop()

def cmd_exit(_):
    sys.exit()

input_handlers = {
    'start': cmd_start,
    'stop': cmd_stop,
    'exit': cmd_exit,
}

def handle_input(raw_input):
    handler = input_handlers.get(raw_input)
    if raw_input == '':
        pass
    elif handler == None:
        print('ERROR: Unknown command')
    else:
        handler(raw_input)

# For debugging purposes
if True:
    cmd_start(None)
    while True:
        pass
else:
    while True:
        raw_input = input('Ƀ  ')
        handle_input(raw_input)
