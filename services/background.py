import threading, time
from core.optimize import optimize
from core.cleaner import clean

def loop():
    from utils.config import load_config, get_whitelist
    config = load_config()
    while True:
        whitelist = get_whitelist()
        optimize(whitelist=whitelist)
        clean()
        time.sleep(config.get('clean_interval', 30))

def start_background():
    threading.Thread(target=loop, daemon=True).start()