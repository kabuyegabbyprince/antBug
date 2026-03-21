import json
import os
from pathlib import Path

CONFIG_PATH = Path('ui/config.json')

DEFAULT_CONFIG = {
    'auto_optimize': True,
    'auto_clean': True,
    'cpu_threshold': 80.0,
    'clean_interval': 30,
    'whitelist': [
        'System Idle Process',
        'svchost.exe',
        'explorer.exe',
        'wininit.exe',
        'chrome.exe',
        'MsMpEng.exe',  # Windows Defender
        'McShield.exe',  # McAfee
        'avp.exe',  # Kaspersky
        'avgui.exe',  # AVG
        'main.py',
        'python.exe'
    ],
    'safe_mode': True
}

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            config.setdefault('safe_mode', True)  # Backwards compat
            return {**DEFAULT_CONFIG, **config}
    return DEFAULT_CONFIG

def save_config(config):
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def get_whitelist():
    return load_config()['whitelist']

def preview_temp_files():
    import tempfile
    temp_dir = Path(tempfile.gettempdir())
    if not temp_dir.exists():
        return []
    return [str(p) for p in temp_dir.rglob('*') if p.is_file()][:50]  # Preview first 50

def preview_high_cpu_processes(threshold):
    import psutil
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            if p.info['cpu_percent'] > threshold:
                procs.append(p.info)
        except:
            pass
    return procs
