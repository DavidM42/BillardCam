from multiprocessing import Process, Value

from data_collection.make_photo import photo_loop

def start_data_collection_p(data_collection_p):
    # creates a photo making process taking up the picam 
    data_collection_p = Process(target=photo_loop) #thanks to https://stackoverflow.com/a/39337670
    data_collection_p.start()
    print("Started data collection continious photos process...")
    return  data_collection_p

def stop_data_collection_p(data_collection_p):
    data_collection_p.terminate()
    data_collection_p.join()
    print("Stopped data collection continious photos process...")
    return  data_collection_p
