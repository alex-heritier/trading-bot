import threading
import time

import socket
import sys
import os

from ticker_daemon import TickerDaemon

ticker = TickerDaemon("config.yml")
t_ticker = threading.Thread(target=ticker.run, daemon=True)
t_ticker.start()

socks = [
    socket.socket(socket.AF_UNIX, socket.SOCK_STREAM),
    socket.socket(socket.AF_UNIX, socket.SOCK_STREAM),
]

# Make sure the socket does not already exist
for sock in socks:
    time.sleep(1)
    sock.connect(ticker.socket_path())

while True:
    for sock in socks:
        data, _ = sock.recvfrom(2048)
        print("[%s] %s"%(sock.fileno(), data.decode("utf-8")))
        sock.close()
        socks.pop(0)
    continue
