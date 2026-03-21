import pystray
from PIL import Image
import threading, sys, subprocess

def start_tray():
    def run():
        image = Image.new('RGB',(64,64),"black")

        def open_ui(icon,item):
            subprocess.Popen(["python","main.py"])

        def quit_app(icon,item):
            icon.stop()
            sys.exit()

        menu = pystray.Menu(
            pystray.MenuItem("Open Dashboard", open_ui),
            pystray.MenuItem("Exit", quit_app)
        )

        icon = pystray.Icon("antiRug", image, "antiRug", menu)
        icon.run()

    threading.Thread(target=run, daemon=True).start()