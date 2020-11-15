import io
import os
from multiprocessing import Process, Value
import time
import datetime
import shutil

#TODO make that configurable via config.py
PHOTO_DELAY = 40

# TODO get this from app.py passend into here maybe
abs_dirname = os.path.dirname(os.path.abspath(__file__)) + "/../imageStates/" # from base project use shots folder for recordings
final_file_name = "fallback_name.mp4" # only fallback uses timestamp

data_collection_last_photo = time.time()

def check_make_photo(camera, any_video_running):
    global data_collection_last_photo

    # take photo only every PHOTO_DELAY seconds
    if time.time() > (data_collection_last_photo + PHOTO_DELAY):
        free = shutil.disk_usage("/")[2]
        gbFree = (free // (2**30))
        if gbFree <= 1:
            #TODO sound alarm and not do it!
            # TODO also port this to continious recording
            pass
        else:
            print("Will save play state as image for data collection...")
            # UTC to ISO 8601 with Local TimeZone information without microsecond  from https://stackoverflow.com/a/28147286
            final_file_name = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() + ".jpg"

            if any_video_running:
                # if shadowplay buffer record or any form of video is running we can't just close camera shutter
                # so specify special things to make quicker less quality images
                # splitter ports https://picamera.readthedocs.io/en/release-1.10/recipes2.html?highlight=splitter_port#recording-at-multiple-resolutions
                # and use video port https://picamera.readthedocs.io/en/release-1.10/recipes2.html?highlight=splitter_port#capturing-images-whilst-recording
                camera.capture(abs_dirname + final_file_name,use_video_port=True)
            else:
                camera.capture(abs_dirname + final_file_name)
            print("Saved play state as image for data collection...")
        data_collection_last_photo = time.time()