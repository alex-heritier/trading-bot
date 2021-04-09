import time
import yaml
import requests
import websockets

import socket
import sys
import os

# Historic Rates - example URL for getting historical price data
# - https://api.pro.coinbase.com/products/btc-usd/candles?start=01-01-2021&end=01-02-2021&granularity=300

class TickerDaemon:
    WAIT_TIME = 2 # seconds

    def __init__(self, config_file):
        print("TickerDaemon - Using config file %s"%config_file)
        with open(config_file, 'r') as stream:
            data = yaml.safe_load(stream)
        self._config = data
        self._socket = self.build_socket(self._config["socket"])
        print("Config: %s"%self._config)

    # Build the communication socket
    def build_socket(self, socket_file):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        # Make sure the socket does not already exist
        try:
            os.unlink(socket_file)
        except OSError:
            if os.path.exists(socket_file):
                raise
        sock.bind(socket_file)
        return sock

    # Main loop
    def run(self):
        while True:
            self.tick()
            time.sleep(TickerDaemon.WAIT_TIME)

    # Run a single tick of the main loop
    def tick(self):
        for ticker_pair in self._config["ticker_pairs"]:
            self.publish_price(ticker_pair)

    # Get price data and then write it on the comm socket
    def publish_price(self, ticker_pair):
        r = requests.get("https://api.coinbase.com/v2/prices/%s/spot"%ticker_pair)
        bytes = str(r.json()).encode('UTF-8')
        self._socket.sendto(bytes, self._config["socket"])
