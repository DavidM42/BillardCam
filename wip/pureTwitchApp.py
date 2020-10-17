from flask import Flask
from flask_oauthlib.client import OAuth
from flask import session, redirect, request, url_for, jsonify
import requests
import json

from twitchApi.TwitchApi import TwitchApi 


##### get config  #####
from config import configuration

# twitch api
client_id = configuration["client_id"]
client_secret = configuration["client_secret"]
broadcaster_id = configuration["broadcaster_id"]

##########

app = Flask(__name__)
app.secret_key = "development"

oauth = OAuth()

twitch = oauth.remote_app('twitch',
                        base_url='https://api.twitch.tv/helix/',
                        request_token_url=None,
                        access_token_method='POST',
                        access_token_url='https://id.twitch.tv/oauth2/token',
                        authorize_url='https://id.twitch.tv/oauth2/authorize',
                        consumer_key=client_id, # get at: https://www.twitch.tv/kraken/oauth2/clients/new
                        consumer_secret=client_secret,
                        request_token_params={'scope': ['user:read:email', 'clips:edit']}
                        )

twitch_api = TwitchApi(client_id, client_secret, twitch.base_url , broadcaster_id)


@app.route('/clipit')
def clipRoute():
    if twitch_api.session_is_broadcaster(session):
        response = twitch_api.create_clip()
        return jsonify(response)
    # elif apiKey in url params:
    #     response = twitch_api.create_clip()
    #     return jsonify(response)
    return "Not permitted to clip. Use valid apikey or login via broadcasters twitch account", 401

@app.route('/login/twitch')
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
    return jsonify(twitch_api.get_user_info()) #other return like control page?

@app.route('/logout')
def logout():
    # TODO revoke token?
    session.pop('twitch_token', None)
    # return redirect(url_for('index'))
    # don't want to endless loop this just logged out and index wants back in
    return "logged out successfully"


if __name__ == '__main__':
    app.run(debug=True, port=8888, host="0.0.0.0")


# TODO write some middleware to shorten repeated twitch session retrieval code
# @twitch.tokengetter
# def get_twitch_token(token=None):
#     return session.get('twitch_token')

# can't use this because stupid twitch decided to require non standard header
# doesn't do right requests with token and client id in header
# me = twitch.get('users')
# if me.status == 200:
#     return jsonify(me.data)
# else:
#     return "error at getting user", me.status