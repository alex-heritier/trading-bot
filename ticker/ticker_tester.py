import threading

import socket
import sys
import os

from ticker import TickerDaemon

ticker = TickerDaemon("config.yml")
t_ticker = threading.Thread(target=ticker.run, daemon=True)
t_ticker.start()

sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
server_address = "tik.s"
# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise
sock.bind(server_address)

while True:
    data, _ = sock.recvfrom(2048)
    print("%s"%data.decode("utf-8"))
    continue
