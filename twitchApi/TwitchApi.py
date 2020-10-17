from urllib.parse import urlencode
import os
import json
from json.decoder import JSONDecodeError
import requests

abs_dirname = os.path.dirname(os.path.abspath(__file__)) + "/"
FILE_PATH = abs_dirname + 'tokens.json'

class TwitchApi():

    def __init__(self, client_id: str, client_secret: str, twitch_base_url: str, broadcaster_id: str):
        self.client_id = client_id
        self.twitch_base_url = twitch_base_url
        self.client_secret = client_secret
        self.broadcaster_id = broadcaster_id

        self.access_token = None
        self.refresh_token = None
        self.read_tokens()

    def save_tokens(self):
        if self.access_token is not None and self.refresh_token is not None:
            # check to only overwrite cache if tokens are really set to something
            data = {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token
            }

            with open(FILE_PATH, 'w+') as outfile:
                json.dump(data, outfile)
        
    def read_tokens(self):
        with open(FILE_PATH, "r") as json_file:
            try:
                data = json.load(json_file)
                if data and data["refresh_token"] and data["access_token"]:
                    self.access_token = data["access_token"]
                    self.refresh_token = data["refresh_token"]
            except JSONDecodeError as e:
                print("No previous valid tokens")
                print(e)

    def check_token_caching(self, access_token: str, refresh_token: str):
        previous_access_token = self.access_token
        previous_refresh_token = self.refresh_token

        self.access_token = access_token
        self.refresh_token = refresh_token
        if self.is_token_by_broadcaster(self.access_token):
            # only cache token for api/alexa clipping if broadcaster account logged in
            self.save_tokens()
        else:
            # reset tokens back to valid tokens of broadcaster account
            self.access_token = previous_access_token
            self.refresh_token = previous_refresh_token

    def is_token_by_broadcaster(self, token: str) -> bool:
        headers = {'Authorization': ("Bearer " + token), 'client-id': self.client_id}# "client-id" in header is important else fails
        r = requests.get(self.twitch_base_url + "users", headers=headers)
        user_info = json.loads(r.text)

        if user_info and user_info["data"] and len(user_info["data"]) > 0 and user_info["data"][0]["id"]:
            if user_info["data"][0]["id"] == self.broadcaster_id:
                return True
        return False

    def session_is_broadcaster(self, session) -> bool:
        if 'twitch_token' in session:
            twitch_token = session["twitch_token"]
            if self.get_user_info(twitch_token)["data"][0]["id"] == self.broadcaster_id:
                return True
        return False

    def validate_access_token(self) -> bool:
        headers = {'Authorization': "OAuth " + self.access_token }# "client-id" in header is important else fails
        r = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)

        # use raise for status here not manual check 
        if r.status_code == 401:
            return False
        elif r.status_code == 200:
            return True

    def revoke_token(self, token: str) -> bool:
        r = requests.post("https://id.twitch.tv/oauth2/revoke?client_id=" + urlencode(self.client_id) + "&token=" + urlencode(token))
        if r.status_code == 200:
            return True
        return False

    def refresh_token(self) -> str:
        r = requests.post("https://id.twitch.tv/oauth2/token?grant_type=refresh_token" +
            "&refresh_token=" + urlencode(self.refresh_token) +
            "&client_id" + urlencode(self.client_id) +
            "&client_secret" + urlencode(self.client_secret)
        )
        if r.status_code == 200:
            return json.loads(r.text)["access_token"]
        return None       

    def get_user_info(self, token) -> dict:
        # if token became invalid try to refresh it
        if not self.validate_access_token():
            self.refresh_token()

        if token is None:
            token = self.access_token

        headers = {'Authorization': ("Bearer " + token), 'client-id': self.client_id}# "client-id" in header is important else fails
        r = requests.get(self.twitch_base_url + "users", headers=headers)
        return json.loads(r.text)

    def create_clip(self) -> dict:
        # if token became invalid try to refresh it
        if not self.validate_access_token():
            self.refresh_token()

        headers = {'Authorization': ("Bearer " + self.access_token), 'client-id': self.client_id } # "client-id" in header is important else fails
        r = requests.post(self.twitch_base_url + "clips?broadcaster_id=" + self.broadcaster_id, headers=headers)
        # TODO if 401 then send some bot message to log in again
        return json.loads(r.text)

    # TODO method to get broadcaster ids?