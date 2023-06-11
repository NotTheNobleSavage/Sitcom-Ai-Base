from flask import Flask, send_file
import base
import os
import base
app = Flask(__name__)

@app.route("/audio", methods=["GET"])
def audio():
    base.run()
    return send_file("output.wav")

@app.route("/script", methods=["GET"])
def script():
    return send_file("script.txt")

app.run(threaded=True)