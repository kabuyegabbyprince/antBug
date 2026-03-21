import psutil
from utils.logger import setup_logger

from utils.config import load_config, get_whitelist

logger = setup_logger()

def optimize(threshold=70.0, whitelist=None):
    config = load_config()
    if config.get('safe_mode', True):
        logger.info("Safe mode enabled - skipping optimize")
        return
    if whitelist is None:
        whitelist = get_whitelist()
    threshold = config.get('cpu_threshold', threshold)
    
    for p in psutil.process_iter(['name','cpu_percent']):
        try:
            if p.info['cpu_percent'] > threshold and p.info['name'] not in whitelist:
                logger.info(f"Terminating {p.info['cpu_percent']:.1f}% {p.info['name']}")
                p.terminate()
        except Exception as e:
            logger.error(str(e))
