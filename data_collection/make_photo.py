import io
import os
from multiprocessing import Process, Value
import time
import datetime
import shutil

# TODO get this from app.py passend into here maybe
abs_dirname = os.path.dirname(os.path.abspath(__file__)) + "/../imageStates/" # from base project use shots folder for recordings
final_file_name = "fallback_name.mp4" # only fallback uses timestamp


def photo_loop():
    # TODO also check that space is free still
    import picamera

    # only initialize cam in function so that it does not already block just by importing
    # methods of this file in main always running flask thread

    with picamera.PiCamera(resolution=(1920, 1080)) as camera:
        while True:
            total, used, free = shutil.disk_usage("/")
            gbFree = (free // (2**30))
            if gbFree <= 1:
                #TODO sound alarm and not do it!
                # TODO also port this to continious recording
                pass
            else:
                print("Will save play state as image for data collection...")
                # UTC to ISO 8601 with Local TimeZone information without microsecond  from https://stackoverflow.com/a/28147286
                final_file_name = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() + ".jpg"
                camera.capture(abs_dirname + final_file_name)
                print("Saved play state as image for data collection...")
            # wait 30 seconds so take a pic every half minute
            #TODO make that configurable via config.py
            time.sleep(40)
