from flask import Flask, redirect, url_for, jsonify, request, session, render_template
from flask_oauthlib.client import OAuth
from functools import wraps
import os
import atexit
import shlex
from multiprocessing import Process, Value
import time
import requests
import json

from streaming.stream_process_control import start_streaming,stop_streaming
from recording.recording_process_control import start_local_recording, stop_local_recording
from recording.circular_saving import trigger_local_clip
from twitchApi.TwitchApi import TwitchApi 

############ CONFIGURATION LOADING ############
from config import configuration

# api access control
api_key = configuration["api_key"]

# for streaming 
stream_key = configuration["stream_key"]
stream_start_file = configuration["stream_start_file"]

# twitch api
client_id = configuration["client_id"]
client_secret = configuration["client_secret"]
broadcaster_id = configuration["broadcaster_id"]
secret_key = configuration["secret_key"]

class ConfigrationException(Exception):
    pass

if not api_key \
    or not stream_key \
    or not stream_start_file \
    or not client_id \
    or not client_secret \
    or not broadcaster_id \
    or not secret_key:
    # TODO maybe more info what is missing and so on
    raise ConfigrationException

############ APP itself and OAuth setup ############

app = Flask(__name__)
app.secret_key = secret_key

oauth = OAuth()

twitch_oauth_scope = {'scope': ['user:read:email', 'clips:edit']}
twitch = oauth.remote_app('twitch',
                base_url='https://api.twitch.tv/helix/',
                request_token_url=None,
                access_token_method='POST',
                access_token_url='https://id.twitch.tv/oauth2/token',
                authorize_url='https://id.twitch.tv/oauth2/authorize',
                consumer_key=client_id,
                consumer_secret=client_secret,
                request_token_params=twitch_oauth_scope
            )

twitch_api = TwitchApi(client_id, client_secret, twitch.base_url , broadcaster_id)

############ Paths for streaming and so on ############

abs_dirname = os.path.dirname(os.path.abspath(__file__)) + "/"

abs_streaming_dir_path = abs_dirname + "streaming/"
streaming_start_command = abs_streaming_dir_path + stream_start_file + " " + stream_key
streaming_start_command = shlex.split(streaming_start_command)

############ Global Vars ############
# global var to indicate if stream is running
running_stream_process = False
# global var containing process to record locally
# get's termianted for streaming
local_record_p = None
stream_multi_p = None

# global var to indicate if a local clip should be created
# use Value class here because shared memory 'b' binary value 
# see https://docs.python.org/3/library/multiprocessing.html#sharing-state-between-processes
save_local_clip = Value('b', False)

############ Routes ############

##### Twitch specific routes #####

# @app.route('/login/twitch')
@app.route('/login')
def login():
    return twitch.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/twitch/authorized')
def authorized():
    resp = twitch.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    access_token = resp['access_token'] # get token and save into session for now
    refresh_token = resp['refresh_token']
    twitch_api.check_token_caching(access_token, refresh_token)
    session['twitch_token'] = access_token
    # return jsonify(twitch_api.get_user_info()) #other return like control page?
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # TODO revoke token?
    # TODO if this was broadcaster account then maybe delete cached account tokens?
    session.pop('twitch_token', None)
    # return redirect(url_for('index'))
    # don't want to endless loop this just logged out and index wants back in
    return jsonify({"status": "Logged out successfully"})


##### General command routes #####

def restricted(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        request_api_key = request.args.get('apikey', type = str)
        is_broadcaster = twitch_api.session_is_broadcaster(session)
        correct_stream_key = request_api_key == api_key

        if not correct_stream_key and not is_broadcaster:
            return jsonify({"status": "error", "message": "Unauthorized. Twitch account of broadcaster must be logged in or correct apikey give in query string"}), 401
        return f(*args, **kwargs)
    return wrapper

# TODO html render website
@app.route("/")
def index():
    if 'twitch_token' in session:
        twitch_token = session["twitch_token"]
        response = twitch_api.get_user_info(twitch_token)
        print(twitch_token)
        print(response)
        #TODO if response {'error': 'Unauthorized', 'status': 401, 'message': 'Invalid OAuth token'} then refresh toke with refresh or relogin
        if response["data"][0]["id"] == twitch_api.broadcaster_id:
            return render_template('index.html', is_stream_running=running_stream_process) 
        return jsonify({"status": "error", "message": "Unauthorized. Twitch account of broadcaster must be logged in NOT any other one"}), 401
    return redirect(url_for('login'))

@app.route("/startStream")
@restricted
def start_stream():
    global running_stream_process
    global local_record_p
    global stream_multi_p

    if not running_stream_process:
        # stop local recording and start livestreaming
        local_record_p = stop_local_recording(local_record_p)
        time.sleep(2) # 2 seconds to really terminate and allow hardware access by other processes
        stream_multi_p = start_streaming(stream_multi_p, streaming_start_command)
        running_stream_process = True
        return jsonify({"status": "Done"})
    else:
        return jsonify({"status": "error", "message": "Already streaming"}), 400

@app.route("/stopStream")
@restricted
def stop_stream():
    global running_stream_process
    global local_record_p
    global save_local_clip
    global stream_multi_p

    if running_stream_process:
        stop_streaming(stream_multi_p)
        running_stream_process = False
        time.sleep(2) # 2 seconds to really terminate and allow hardware access by other processes
        local_record_p = start_local_recording(local_record_p, save_local_clip)
        return jsonify({"status": "Done"})
    else:
        return jsonify({"status": "error", "message": "Stream not running"}), 400

@app.route("/clipit")
@restricted
def clip_it():
    global running_stream_process
    global save_local_clip

    if running_stream_process:
        response = twitch_api.create_clip()
        return jsonify(response)
        # return jsonify({"status": "Saved on twitch"})
    else:
        trigger_local_clip(save_local_clip)
        return jsonify({"status": "Locally saved"})


############ Start and stop logic ############

def exit_handler():
    # always make a clean exit and terminate both streaming and local recording processes
    if running_stream_process:
        # always stop streaming if file ends (and power is not cut...)
        stop_streaming(stream_multi_p)
    else:
        # else stop local recording
        stop_local_recording(local_record_p)
    
if __name__ == "__main__":
    atexit.register(exit_handler)

    local_record_p = start_local_recording(local_record_p, save_local_clip)
    # TODO make port config var
    app.run(debug=True, port=8888, host="0.0.0.0", use_reloader=False)
