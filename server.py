from flask import Flask, send_file, abort, g
import base
import os
import time
import io
import threading

# Function to start the base.run_que() in a separate thread
base.cleanup()
def run_in_background():
    base.run_que()

# Start a new thread to run base.run_que() in the background
thread = threading.Thread(target=run_in_background, daemon=True)
thread.start()

app = Flask(__name__)

@app.route("/audio", methods=["GET"])
def audio():
    files = [files for files in os.listdir(os.getcwd()) if files.startswith("output")]
    if not files: # If no files exist, return a message
        return "No output files found"
    return_data = io.BytesIO()
    with open(files[0], 'rb') as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    os.remove(files[0])
    return send_file(return_data, mimetype="audio/wav")

@app.route("/script", methods=["GET"])
def script():
    files = [files for files in os.listdir(os.getcwd()) if files.startswith("script")]
    if not files: # If no files exist, return a message
        return "No script files found"
    return_data = io.BytesIO()
    with open(files[0], 'rb') as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    os.remove(files[0])
    return send_file(return_data, mimetype="text/plain")

app.run(threaded=True, debug=True)