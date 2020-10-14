from multiprocessing import Process, Value

from recording.circular_saving import record_loop

def start_local_recording(local_record_p, save_local_clip):
    # creates a local record process taking up the picam 
    local_record_p = Process(target=record_loop, args=(save_local_clip,)) #thanks to https://stackoverflow.com/a/39337670
    local_record_p.start()
    print("Started local circular recording process...")
    return local_record_p

def stop_local_recording(local_record_p):
    local_record_p.terminate()
    local_record_p.join()
    print("Stopped local circular recording process...")
    return local_record_p
