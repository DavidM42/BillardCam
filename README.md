# BillardCam 🎱

This project runs on a RaspberryPi with a connected Raspberry Pi HQ Camera equipped with a [130 Degree M12 lens by Arducam](https://www.arducam.com/product/arducam-130-degree-ultra-wide-angle-1-2-3-m12-mount-with-lens-adapter-for-raspberry-pi-high-quality-camera/) (or any other compatible lens with enough fov to cover the table).
<!-- TODO upload camera mount as step and stl to thingiverse  and link here-->
It is currently mounted with 3D printed parts in the lamp above my Billard table.
This project allows me to stream the gameplay happening on the table to online services (at the moment twitch but potentially also youtube or others supporting rtmp streaming).
With this project no cool shot will ever be missed because you can create clips of every moment *after* it happened.

It's always running continous recording so you can always record clips to your sd card and while your streaming twitch clips will be created if you wish to save a shot.

The streaming can be started/stopped via a *web interface* or via a *REST-API* with an apiKey. Clips can also be created via the web interface or a GET api request.
For twitch clips to be created you have to log into the web interface with your broadcaster twitch account at least once for it to save the oauth tokens.

You can also combine the REST-API with e.g. ifft to create clips by yelling at Alexa.

<!-- TODO instructions on how to setup twitch oauth app to use with this -->
<!-- TODO instructions to iftt webhook usage -->
<!-- TODO test out writing an alexa app again with new short intents to use with this? -->

## Getting started
1. Make python3 virtualenv `virtualenv -p python3 venv`
2. Activate it `source venv/bin/activate`
3. Install requirements.txt via `pip install -r ./requirements.txt`
4. Copy `config.py.example` to `config.py` and enter your twitch stream and api_key
5. Run dev flask server via `python ./app.py`


## Autostart on boot
1. Create service via: `sudo systemctl --force --full edit billardcam.service` and paste

```
[Unit]
Description=Starts control server to stream billard and save clips
After=network.target

[Service]
ExecStart=/home/pi/billardCamProject/venv/bin/python /home/pi/billardCamProject/app.py
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```
_(Maybe you have to edit the paths to your virtual-environment and the `app.py` file if you cloned the repo to a different path)_

2. Reload services via `sudo systemctl daemon-reload`
3. Enable autostart of service: `sudo systemctl enable billardcam.service`

## Security
This app *saves unencrypted access key to your broadcaster twitch account to disk*. This is a security risk.
Only install on machines you and only you fully control be aware of this risk.