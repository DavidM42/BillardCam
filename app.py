from flask import Flask, redirect, url_for, jsonify, request
import os
from stream_process_control import start_streaming,stop_streaming
import atexit
import shlex
from config import configuration


###### CONFIGURATION LOADING ##########
api_key = configuration["api_key"]
stream_key = configuration["stream_key"]
stream_start_file = configuration["stream_start_file"]

class ConfigrationException(Exception):
    pass

if not api_key or not stream_key or not stream_start_file:
    # TODO maybe more info what is missing and so on
    raise ConfigrationException

####### APP itself ####################

app = Flask(__name__)

abs_dirname = os.path.dirname(os.path.abspath(__file__)) + "/"

streaming_start_command = abs_dirname + stream_start_file + " " + stream_key
streaming_start_command = shlex.split(streaming_start_command)

running_stream_process = False

# TODO html render website
@app.route("/")
def index():
    return "ok"


@app.route("/startStream")
def startStream():
    global running_stream_process
    
    request_api_key = request.args.get('apikey', type = str)
    if request_api_key and request_api_key == api_key:
        if not running_stream_process:
            running_stream_process = start_streaming(streaming_start_command)
            return jsonify({"status": "Done"})
        else:
            return jsonify({"status": "error", "message": "Already exists"}), 400
    else:
        return jsonify({"status": "error", "message": "Unauthorized missing apiKey"}), 401

@app.route("/stopStream")
def stopStream():
    global running_stream_process

    request_api_key = request.args.get('apikey', type = str)
    if request_api_key and request_api_key == api_key:
        if running_stream_process:
            stop_streaming(running_stream_process)
            running_stream_process = False
            return jsonify({"status": "Done"})
        else:
            return jsonify({"status": "error", "message": "Stream not running"}), 400
    else:
        return jsonify({"status": "error", "message": "Unauthorized missing apiKey"}), 401

@app.route("/clipit")
def clipit():
    global running_stream_process

    request_api_key = request.args.get('apikey', type = str)
    if request_api_key and request_api_key == api_key:
        if running_stream_process:
            #TODO clip request making
            return jsonify({"status": "Done"})
        else:
            return jsonify({"status": "error", "message": "Stream not running"}), 400
    else:
        return jsonify({"status": "error", "message": "Unauthorized missing apiKey"}), 401








# always stop streaming if file ends (and power is not cut...)
def exit_handler():
    if running_stream_process:
        stop_streaming(running_stream_process)

if __name__ == "__main__":
    atexit.register(exit_handler)
    app.run(debug=True, port=8888, host="0.0.0.0")