from flask import Flask, send_file
import base
import os
app = Flask(__name__)

#Create an endpoint that endpoint is going to be POST it is going to recive a JSON object with a prompt, send that prompt to spongebob.py and return the audio file
@app.route("/spongebob", methods=["POST"])
def spongebob():
    prompt = Flask.request.json["prompt"]
    spongebob.generate(prompt)
    return Flask.send_file("output.wav")

@app.route("/audio", methods=["GET"])
def audio():
    print('hi')
    return send_file("output.wav")

app.run(threaded=True)