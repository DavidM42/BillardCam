# BillardPlayCam

TODO write up


## Getting started
1. Make python3 virtualenv `virtualenv -p python3 venv`
2. Activate it `source venv/bin/activate`
3. Install requirements.txt via `pip install -r ./requirements.txt`
4. Copy `config.py.example` to `config.py` and enter your twitch stream and api_key
5. Run dev flask server via `python ./app.py`


## Security
This app *saves unencrypted access key to your broadcaster twitch account to disk*. This is a security risk.
Only install on machines you and only you fully control be aware of this risk.