import subprocess
import os
import signal
from multiprocessing import Process, Value

# TODO function docs
def start_stream_command(streaming_start_command):
    print("Starting streaming...")
    # TODO make configurable wether with or without mic and if with internet radio music
    # pipe stdout to null so that write buffer does not overflow and kill (after 4mims) see https://stackoverflow.com/a/62279468/7692491
    subpr = subprocess.Popen(streaming_start_command, shell=False, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)

def stop_streaming(stream_multi_p):
    # stop streaming by emitting sigint which is basically pressing strg+c
    print("Stopping stream...")
    # got stop magic from https://stackoverflow.com/a/22582602
    stream_multi_p.terminate()
    stream_multi_p.join()
    return stream_p

def start_streaming(stream_multi_p, streaming_start_command):
    # creates a seperate stream process 
    stream_multi_p = Process(target=start_stream_command, args=(streaming_start_command,)) #thanks to https://stackoverflow.com/a/39337670
    stream_multi_p.start()
    return stream_multi_p
