import subprocess
import os
import signal

# TODO function docs
def start_streaming(streaming_start_command):
    print("Starting streaming...")
    # TODO make configurable wether with or without mic and if with internet radio music
    return subprocess.Popen(streaming_start_command, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

def stop_streaming(stream_process):
    # stop streaming by emitting sigint which is basically pressing strg+c
    print("Stopping stream...")
    # got stop magic from https://stackoverflow.com/a/22582602
    os.killpg(os.getpgid(stream_process.pid), signal.SIGTERM)