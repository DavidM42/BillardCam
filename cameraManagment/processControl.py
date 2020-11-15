from multiprocessing import Process

from cameraManagment.cameraManagment import camera_manager_loop
from cameraManagment.cameraConfiguration import CameraConfiguration

from featureStates.featureStates import FeatureStates

def start_camera_managment(feature_states: FeatureStates, camera_configuration: CameraConfiguration):
    # creates a camera managment process taking up the picam 
    camera_manager_p = Process(target=camera_manager_loop, args=(feature_states,camera_configuration,)) #thanks to https://stackoverflow.com/a/39337670
    camera_manager_p.start()
    print("Started camera manager process...")
    return camera_manager_p

def stop_camera_managment(camera_manager_p):
    camera_manager_p.terminate()
    camera_manager_p.join()
    print("Stopped camera manager process...")
    return camera_manager_p