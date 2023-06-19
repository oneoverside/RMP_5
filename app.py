import threading

from TempUpdater.TempUpdater import start
from WebAppFlask.WebAppFlask import app
from tkinter_block.tkinter_block import start_tinker

updater = threading.Thread(target=start, daemon=True).start()
web = threading.Thread(target=app.run, daemon=True).start()
tkapp = threading.Thread(target=start_tinker, daemon=True).start()
