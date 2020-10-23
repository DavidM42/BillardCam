import subprocess
import os
import signal
from multiprocessing import Process, Value

# TODO function docs
def start_streaming(streaming_start_command):
    print("Starting streaming...")
    # TODO make configurable wether with or without mic and if with internet radio music
    # pipe stdout to null so that write buffer does not overflow and kill (after 4mims) see https://stackoverflow.com/a/62279468/7692491
    # subpr = subprocess.Popen(streaming_start_command, shell=False, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    # while True:
        # pass
    # trying less sophisticated more basic version now
    # system_input = streaming_start_command + " &>/dev/null &"
    system_input = streaming_start_command + " &>/home/pi/stream.log &"
    # print(system_input)
    os.system(system_input)


def stop_streaming():
    print("Stopping stream...")
    # system_input = streaming_stop_command + " &>/dev/null &"
    system_input = streaming_stop_command + " &>/home/pi/stream.log &"
    # print(system_input)
    os.system(system_input)
    # return stream_p

