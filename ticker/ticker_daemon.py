import threading
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

### PRIVATE

    def __init__(self, config_file):
        # Load config file
        print("TickerDaemon - Using config file %s"%config_file)
        with open(config_file, 'r') as stream:
            data = yaml.safe_load(stream)
        print("Config: %s"%data)

        # Init variables
        self._config = data
        self._in_socket = self._build_in_socket(self._config["socket"])
        self._in_thread = threading.Thread(target=self._listen_for_clients, daemon=True)
        self._client_conns = []

        # Start listener thread
        self._in_thread.start()

    # Build the input socket
    def _build_in_socket(self, socket_file):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # Make sure the socket does not already exist
        try:
            os.unlink(socket_file)
        except OSError:
            if os.path.exists(socket_file):
                raise
        sock.bind(socket_file)
        sock.listen(1)
        return sock

    def _listen_for_clients(self):
        while True:
            # Wait for a connection
            connection, client_address = self._in_socket.accept()
            print("New client [%s]"%connection.fileno())
            self._client_conns.append(connection)

    # Run a single tick of the main loop
    def _tick(self):
        for ticker_pair in self._config["ticker_pairs"]:
            self._publish_price(ticker_pair)

    # Get price data and then write it on the output socket
    def _publish_price(self, ticker_pair):
        r = requests.get("https://api.coinbase.com/v2/prices/%s/spot"%ticker_pair)
        bytes = str(r.json()).encode('UTF-8')
        for conn in self._client_conns:
            try:
                conn.sendall(bytes)
            except BrokenPipeError:
                print("Client disconnected [%s]"%conn.fileno())
                self._client_conns.remove(conn)

### PUBLIC

    def socket_path(self):
        return self._config["socket"]

    # Main loop
    def run(self):
        while True:
            self._tick()
            time.sleep(TickerDaemon.WAIT_TIME)
