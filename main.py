# import os
# import eel
# from engine import *
# from engine.features import *
# from engine.command import *

# eel.init("www")

# os.system('start msedge.exe --app="http://localhost:8080/home.html"')

# eel.start('home.html', mode=None, host='localhost', port=8080, block=True)




import sys
import os

# Ensure Python can find `app.py` inside `www/`
sys.path.append(os.path.join(os.path.dirname(__file__), "www"))

from app import app  # Now Python should find app.py

import multiprocessing
import eel
from engine import *
from engine.features import *
from engine.command import *

eel.init("www")

# Function to run Flask
def run_flask():
    print("Starting Flask API...")
    app.run(host="127.0.0.1", port=5000, debug=False)  # Flask runs on port 5000

# Function to run Eel
def run_eel():
    print("Starting Eel...")
    os.system('start msedge.exe --app="http://localhost:8080/index.html"')
    eel.start('index.html', mode=None, host='localhost', port=8080, block=True)  # Eel runs on port 8080

if __name__ == "__main__":
    # Create separate processes for Flask and Eel
    flask_process = multiprocessing.Process(target=run_flask)
    eel_process = multiprocessing.Process(target=run_eel)

    # Start both processes
    flask_process.start()
    eel_process.start()

    # Wait for Eel to finish first (GUI app)
    eel_process.join()

    # If Eel is closed, also stop Flask
    if flask_process.is_alive():
        flask_process.terminate()
        flask_process.join()

    print("Both Flask and Eel have stopped.")

