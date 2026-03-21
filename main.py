from services.background import start_background
from tray.tray import start_tray
from ui.dashboard_fixed import run_ui
from utils.logger import setup_logger

logger = setup_logger()

if __name__ == "__main__":
    logger.info("Starting antiRug Enterprise")
    import threading
    threading.Thread(target=start_background, daemon=True).start()
    threading.Thread(target=start_tray, daemon=True).start()
    run_ui()
