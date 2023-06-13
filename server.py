from flask import Flask, send_file
import base
import os
import base
app = Flask(__name__)

base.cleanup()
@app.route("/audio", methods=["GET"])
def audio():
    base.run()
    if os.path.exists("output.wav"):
        return send_file("output.wav")
    else:
        return "Error"

@app.route("/script", methods=["GET"])
def script():
    return send_file("script.txt")

app.run(threaded=True)