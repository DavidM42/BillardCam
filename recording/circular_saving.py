import io
import os
from multiprocessing import Process, Value
import time
import datetime

# TODO get this from app.py passend into here maybe
abs_dirname = os.path.dirname(os.path.abspath(__file__)) + "/../shots/" # from base project use shots folder for recordings
stream_save = abs_dirname + 'saved_shot.h264'
final_file_name = "fallback_name.mp4" # only fallback uses timestamp


def record_loop(save_video):
    import picamera

    # only initialize cam in function so that it does not already block just by importing
    # methods of this file in main always running flask thread
    camera = picamera.PiCamera()
    # TODO configurable clip length in config.py
    stream = picamera.PiCameraCircularIO(camera, seconds=10)
    camera.start_recording(stream, format='h264')

    try:
        while True:
            camera.wait_recording(1)
            if save_video.value == True:
                print("Will save video clip locally now...")
                # Keep recording for 5 seconds and only then write the
                # stream to disk
                camera.wait_recording(5)
                stream.copy_to(stream_save)
                
                # UTC to ISO 8601 with Local TimeZone information without microsecond  from https://stackoverflow.com/a/28147286
                final_file_name = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() + ".mp4"

                os.system("MP4Box -add " +  stream_save + " " + abs_dirname + final_file_name)
                os.system("rm " + stream_save)
                print("Saved video locally...")
    finally:
        camera.stop_recording()


def trigger_local_clip(save_video):
    # this shared variable is also in local recording multiprocess
    # if is true in multiprocess then save so temp set it true for 1.15 seconds then back off
    save_video.value = True
    time.sleep(1.15)
    save_video.value = False