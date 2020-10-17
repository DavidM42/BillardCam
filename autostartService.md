# Autostart project as service

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

2. Reload services via `sudo systemctl daemon-reload`
3. Enable autostart of service: `sudo systemctl enable billardcam.service`




