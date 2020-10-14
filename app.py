from flask import Flask, redirect, url_for, jsonify, request
import os
import atexit
import shlex
from multiprocessing import Process, Value
import time

from streaming.stream_process_control import start_streaming,stop_streaming
from recording.recording_process_control import start_local_recording, stop_local_recording
from recording.circular_saving import trigger_local_clip

###### CONFIGURATION LOADING ##########
from config import configuration

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



# streaming paths and commands
abs_streaming_dir_path = abs_dirname + "streaming/"
streaming_start_command = abs_streaming_dir_path + stream_start_file + " " + stream_key
streaming_start_command = shlex.split(streaming_start_command)

######### Global Vars ##############
# global var to indicate if stream is running
running_stream_process = False
# global var containing process to record locally
# get's termianted for streaming
local_record_p = None

# global var to indicate if a local clip should be created
# use Value class here because shared memory 'b' binary value 
# see https://docs.python.org/3/library/multiprocessing.html#sharing-state-between-processes
save_local_clip = Value('b', False)

########## Routes ###############

# TODO html render website
@app.route("/")
def index():
    return "ok"


@app.route("/startStream")
def startStream():
    global running_stream_process
    global local_record_p

    request_api_key = request.args.get('apikey', type = str)
    if request_api_key and request_api_key == api_key:
        if not running_stream_process:
            # stop local recording and start livestreaming
            local_record_p = stop_local_recording(local_record_p)
            time.sleep(2) # 2 seconds to really terminate and allow hardware access by other processes
            running_stream_process = start_streaming(streaming_start_command)
            return jsonify({"status": "Done"})
        else:
            return jsonify({"status": "error", "message": "Already exists"}), 400
    else:
        return jsonify({"status": "error", "message": "Unauthorized missing apiKey"}), 401

@app.route("/stopStream")
def stopStream():
    global running_stream_process
    global local_record_p
    global save_local_clip

    request_api_key = request.args.get('apikey', type = str)
    if request_api_key and request_api_key == api_key:
        if running_stream_process:
            stop_streaming(running_stream_process)
            running_stream_process = False
            time.sleep(2) # 2 seconds to really terminate and allow hardware access by other processes
            local_record_p = start_local_recording(local_record_p, save_local_clip)
            return jsonify({"status": "Done"})
        else:
            return jsonify({"status": "error", "message": "Stream not running"}), 400
    else:
        return jsonify({"status": "error", "message": "Unauthorized missing apiKey"}), 401

@app.route("/clipit")
def clipit():
    global running_stream_process
    global save_local_clip

    request_api_key = request.args.get('apikey', type = str)
    if request_api_key and request_api_key == api_key:
        if running_stream_process:
            #TODO clip request making on twitch integrating
            return jsonify({"status": "Saved on twitch"})
        else:
            trigger_local_clip(save_local_clip)
            return jsonify({"status": "Locally saved"})
    else:
        return jsonify({"status": "error", "message": "Unauthorized missing apiKey"}), 401





def exit_handler():
    # always make a clean exit and terminate both streaming and local recording processes
    if running_stream_process:
        # always stop streaming if file ends (and power is not cut...)
        stop_streaming(running_stream_process)
    else:
        # else stop local recording
        stop_local_recording(local_record_p)
    
if __name__ == "__main__":
    atexit.register(exit_handler)

    local_record_p = start_local_recording(local_record_p, save_local_clip)
    app.run(debug=True, port=8888, host="0.0.0.0", use_reloader=False)
