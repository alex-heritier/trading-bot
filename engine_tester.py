import threading
import yaml

from engine import engine

with open("config/engine.yml", 'r') as stream:
    data = yaml.safe_load(stream)

engine = engine.Daemon(data)
t_engine = threading.Thread(target=engine.run, daemon=True)
t_engine.start()

while True:
    continue
