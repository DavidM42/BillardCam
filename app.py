from flask import Flask, redirect, url_for, jsonify, request, session, render_template
from flask_oauthlib.client import OAuth, OAuthException
from functools import wraps
import os
import atexit
import shlex
from multiprocessing import Process, Value
import time
import requests
import json

# concurrency stuff
import multiprocessing
from multiprocessing.managers import BaseManager


from cameraManagment.processControl import start_camera_managment, stop_camera_managment
from cameraManagment.cameraConfiguration import CameraConfiguration

from recording.circular_saving import save_local_buffer
from data_collection.data_collector import check_make_photo
from twitchApi.TwitchApi import TwitchApi 
from featureStates.featureStates import FeatureStates


############ CONFIGURATION LOADING ############
from config import configuration

# api access control
api_key = configuration["api_key"]

# for streaming 
stream_key = configuration["stream_key"]
stream_ingest_url = configuration["stream_ingest_url"]
mic_input = configuration["mic_input"]
radio_url = configuration["radio_url"]

# for stream to ml analyzer
ml_stream_url = configuration["ml_stream_url"]

# twitch api
client_id = configuration["client_id"]
client_secret = configuration["client_secret"]
broadcaster_id = configuration["broadcaster_id"]
secret_key = configuration["secret_key"]

class ConfigrationException(Exception):
    pass

if not api_key \
    or not stream_key \
    or not stream_ingest_url \
    or not mic_input \
    or not radio_url \
    or not ml_stream_url \
    or not client_id \
    or not client_secret \
    or not broadcaster_id \
    or not secret_key:
    # TODO maybe more info what is missing and so on
    raise ConfigrationException


############ Multiprocessing manager for shared objects ############

# setup manager for multiprocessing data coordination
class DataManager(BaseManager):
    pass

DataManager.register('FeatureStates', FeatureStates)
DataManager.register('CameraConfiguration', CameraConfiguration)
manager = DataManager()
manager.start()

feature_states = manager.FeatureStates() # pylint: disable=no-member
camera_configuration = manager.CameraConfiguration(stream_ingest_url, stream_key, ml_stream_url, mic_input, radio_url) # pylint: disable=no-member

############ Start camera manager instance to manage all the recording ############

camera_manager_p = start_camera_managment(feature_states, camera_configuration)

############ APP itself and OAuth setup ############

# TODO favicon for app and maybe pwa manifest.json

app = Flask(__name__)
app.secret_key = secret_key

# TODO via config py and fix this
#app.config['SERVER_NAME'] = "https://billard.merzlabs.de"

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


############ Routes ############

##### Twitch specific routes #####

# @app.route('/login/twitch')
@app.route('/login')
def login():
    # TODO FIX
    # return twitch.authorize(callback=url_for('authorized', _external=True))
    return twitch.authorize(callback="https://billard.merzlabs.de/login/twitch/authorized")

@app.route('/login/twitch/authorized')
def authorized():
    try:
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
    except OAuthException:
        print("Invalid Oauth exception from twitch")
        # trying login again
        # maybe error better
        return redirect(url_for('login'))

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
        correct_api_key = request_api_key == api_key

        if not correct_api_key and not is_broadcaster:
            return jsonify({"status": "error", "message": "Unauthorized. Twitch account of broadcaster must be logged in or correct apikey given in query string"}), 401
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    if 'twitch_token' in session:
        twitch_token = session["twitch_token"]
        response = twitch_api.get_user_info(twitch_token)
        #TODO if response {'error': 'Unauthorized', 'status': 401, 'message': 'Invalid OAuth token'} then refresh toke with refresh or relogin
        if response and "data" in response and response["data"][0]["id"] == twitch_api.broadcaster_id:
            return render_template('index.html',
                feature_states = feature_states.toFlagDict()
            ) 
        return jsonify({"status": "error", "message": "Unauthorized. Twitch account of broadcaster must be logged in NOT any other one"}), 401
    return redirect(url_for('login'))

@app.route("/updateFeatures", methods=['POST'])
@restricted
def updateFeatures():
    print("Updating current features...")
    try:
        feature_states.fromFlagDict(request.json)    
        return jsonify({"status": "Done"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Missing: " + str(e)}), 400

@app.route("/clipit")
@restricted
def clip_it():
    global feature_states

    if feature_states.get_STREAMING()[0] and feature_states.get_SHADOWPLAY():
        # make request for local shadowplay
        feature_states.set_shadowplay_request(True)

        # also make twitch clip
        response = twitch_api.create_clip()
        return jsonify({"status": "Saved locally and to twitch", "twitchResponse": response})

    elif feature_states.get_SHADOWPLAY():
        feature_states.set_shadowplay_request(True)
        return jsonify({"status": "Locally saved"})

    elif feature_states.get_STREAMING()[0]:
        response = twitch_api.create_clip()
        return jsonify({"status": "Saved to twitch", "twitchResponse": response})

    else:
        # TODO status code 500 here
        return jsonify({"error": "Neither streaming to twitch nor local recording is active"})

@app.route("/twitchUser")
def twitch_user_info():
    if 'twitch_token' in session:
        twitch_token = session["twitch_token"]
        response = twitch_api.get_user_info(twitch_token)
        return jsonify(response)
    return redirect(url_for('login'))

############ Start and stop logic ############

def exit_handler():
    print("Cleaning up all processes and exiting...")
    # always make a clean exit and terminate both streaming and local recording processes
    stop_camera_managment(camera_manager_p)

if __name__ == "__main__":
    atexit.register(exit_handler)

    # TODO make port config var
    app.run(debug=True, port=8888, host="0.0.0.0", use_reloader=False)
