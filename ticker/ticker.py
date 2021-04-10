import threading
import time

import socket
import sys
import os

from helper import coinbase

class Daemon:
    WAIT_TIME = 10 # seconds

### PRIVATE

    def __init__(self, config_data):
        # Init variables
        self._is_running = True
        self._config = config_data
        self._in_socket = self._build_in_socket(config_data["socket"])
        self._in_thread = threading.Thread(target=self._listen_for_clients, daemon=True)
        self._client_conns = []

        # Start listener thread
        self._in_thread.start()

    def __del__(self):
        self._is_running = False

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
        sock.listen(4)
        return sock

    # Listen for incoming clients
    def _listen_for_clients(self):
        while True:
            # Wait for a connection
            connection, client_address = self._in_socket.accept()
            print("[Ticker] new client [%s]"%connection.fileno())
            self._client_conns.append(connection)

    # Run a single tick of the main loop
    def _tick(self):
        for ticker_pair in self._config["ticker_pairs"]:
            self._publish_price(ticker_pair)

    # Get price data and send it to connected clients
    def _publish_price(self, ticker_pair):
        r = coinbase.get_ticker_price(ticker_pair)
        msg = "{%s} %s"%(ticker_pair, str(r.json()))
        for conn in self._client_conns:
            try:
                conn.sendall(msg.encode('UTF-8'))
            except BrokenPipeError:
                print("[Ticker] client disconnected [%s]"%conn.fileno())
                self._client_conns.remove(conn)

### PUBLIC

    def socket_path(self):
        return self._config["socket"]

    # Main loop
    def run(self):
        while self._is_running:
            self._tick()
            time.sleep(Daemon.WAIT_TIME)
