import threading
import time

import socket
import sys
import os

from ticker import ticker
from helper import coinbase

class Daemon:
    WAIT_TIME = 1 # seconds

### PRIVATE

    def __init__(self, config_data):
        self._config = config_data

    # Build the input socket
    def _build_ticker_listener_socket(self, socket_file):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        while True:
            try:
                sock.connect(socket_file)
                break;
            except:
                print("Connection Failed, Retrying..")
                time.sleep(1)
        return sock

    # Listen for incoming ticker data
    def _listen_for_ticker(self):
        while True:
            data, _ = self._ticker_listen_socket.recvfrom(2 ** 14)
            print("etl[%s] %s"%(self._ticker_listen_socket.fileno(), data.decode("utf-8")))

    # Setup ticker and ticker listener threads
    def _setup_ticker(self):
        # Ticker runner thread
        self._ticker = ticker.Daemon({
            "provider": self._config["provider"],
            "socket": self._config["ticker_socket"],
            "ticker_pairs": self._config["ticker_pairs"],
        })
        self._t_ticker = threading.Thread(target=self._ticker.run, daemon=True)
        self._t_ticker.start()

        # Ticker listener thread
        self._ticker_listen_socket = self._build_ticker_listener_socket(self._ticker.socket_path())
        self._t_ticker_listener = threading.Thread(target=self._listen_for_ticker, daemon=True)
        self._t_ticker_listener.start()

    # Initialize historic data for calculating indicators
    def _setup_historic_data(self):
        tickers = self._config["ticker_pairs"]
        for ticker in tickers:
            historic_data = coinbase.get_historical_rates(ticker, granularity="300").json()
            print(historic_data)

    # Run a single tick of the main loop
    def _tick(self):
        print("Thinking...")

### PUBLIC

    def run(self):
        self._setup_ticker()
        self._setup_historic_data()

        # Main loop
        while True:
            self._tick()
            time.sleep(Daemon.WAIT_TIME)
