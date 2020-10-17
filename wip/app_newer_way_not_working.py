from flask import Flask, redirect, url_for
from flask_dance import OAuth2ConsumerBlueprint
import os


app = Flask(__name__)
app.secret_key = "XXXXX"

client_id = "XXXXX"
client_secret = "XXXXXX"

scope = ('user:read:email', 'clips:edit')
# redirect_url= "http://merzlabs:de:8888/login/twitch/authorized"
redirect_url= "http://localhost:8888/login/twitch/authorized"

# while using localhost without https
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


twitch_bp = OAuth2ConsumerBlueprint(
        "twitch",
        __name__,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        base_url="https://api.twitch.tv/helix/",
        authorization_url="https://id.twitch.tv/oauth2/authorize",
        token_url="https://id.twitch.tv/oauth2/token",
        redirect_url=redirect_url,
        # redirect_to=redirect_to,
        # login_url=login_url,
        # authorized_url=authorized_url,
        # session_class=session_class,
        # storage=storage,
        token_url_params={"include_client_id": True}
    )

app.register_blueprint(twitch_bp, url_prefix="/login")

@app.route("/")
def index():
    twitch = twitch_bp.session

    # if not twitch.authorized:
    #     return redirect(url_for("twitch.login"))

    twitch_user_info = twitch.get("users").json()
    return twitch_user_info    
    # print("You are {username} on Twitch".format(username=twitch_user_info['data'][0]['display_name']))

if __name__ == "__main__":
    app.run(debug=True, port=8888, host="0.0.0.0")