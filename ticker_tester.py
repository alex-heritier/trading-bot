import threading
import time
import random

import socket
import sys
import os

from ticker import ticker

CLIENT_COUNT = 1

ticker = ticker.daemon("config/ticker.yml")
t_ticker = threading.Thread(target=ticker.run, daemon=True)
t_ticker.start()

socks = []
for _ in range(CLIENT_COUNT):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    while True:
        try:
            sock.connect(ticker.socket_path())
            socks.append(sock)
            break;
        except:
            print("Connection Failed, Retrying..")
            time.sleep(1)

while True:
    for sock in socks:
        data, _ = sock.recvfrom(2 ** 14)
        print("l[%s] %s"%(sock.fileno(), data.decode("utf-8")))
