import io
import os
from multiprocessing import Process, Value
import time
import datetime
from math import ceil
from picamera import PiCameraCircularIO

# TODO get this from app.py into here maybe
abs_dirname = os.path.dirname(os.path.abspath(__file__)) + "/../shots/" # from base project use shots folder for recordings
stream_save = abs_dirname + 'saved_shot.h264'
final_file_name = "fallback_name.mp4" # only fallback uses timestamp

def start_buffer_recording(camera, BITRATE, SHADOWPLAY_TIME):
    print("Creating shadowplay circular buffer...")
    shadowplay_stream = PiCameraCircularIO(camera, seconds=ceil(SHADOWPLAY_TIME/4.2)) #divide by 4 because bitrate is so low it would record way more (fourth of normal bitrate so 10s buffer would actually be 40s)
    camera.start_recording(shadowplay_stream, format='h264', bitrate=BITRATE, splitter_port=1) #,bitrate=BITRATE) #,splitter_port=2)
    return shadowplay_stream

def save_local_buffer(camera, buffer_stream):
    # Keep recording for 5 seconds and only then write the
    # stream to disk
    camera.wait_recording(2)
    buffer_stream.copy_to(stream_save)
    
    # UTC to ISO 8601 with Local TimeZone information without microsecond  from https://stackoverflow.com/a/28147286
    final_file_name = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() + ".mp4"

    # : illegal character in filenames so replace that
    final_file_name = final_file_name.replace(':', '_')

    os.system("MP4Box -add " +  stream_save + " " + abs_dirname + final_file_name)
    os.system("rm " + stream_save)
    print("Saved video locally...")
