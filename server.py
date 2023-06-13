from flask import Flask, send_file
import base
import os
import base
import logging

#Settup up logging
logging.basicConfig(filename='test.log', encoding='utf-8', level=logging.DEBUG)

app = Flask(__name__)

base.cleanup()
@app.route("/audio", methods=["GET"])
def audio():
    logging.info("Audio Requested")
    base.run()
    try:
        return send_file("output.wav")
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending audio: {e}")
        return 

@app.route("/script", methods=["GET"])
def script():
    logging.info("Script Requested")
    try:
        return send_file("script.txt")
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending script: {e}")
        return

app.run(threaded=True)