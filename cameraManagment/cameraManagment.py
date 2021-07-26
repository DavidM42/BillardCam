from picamera import PiCamera
import ffmpeg
from picamera.exc import PiCameraNotRecording
import time

from featureStates.featureStates import FeatureStates
from cameraManagment.cameraConfiguration import CameraConfiguration
from recording.circular_saving import start_buffer_recording, save_local_buffer
from data_collection.data_collector import check_make_photo

RADIO_OFFSET = 1.1

# not needed anymore synced it
# MIC_OFFSET = 0

class CameraManagment:
    def __init__(self, feature_states: FeatureStates, camera_configuration: CameraConfiguration):
        self.feature_states = feature_states
        self.camera_configuration = camera_configuration

        self.any_video_running = False
        self.stream_runner_p = None
        self.camera = PiCamera(framerate=self.camera_configuration.get_framerate())
        self.camera.resolution = self.camera_configuration.get_resolution()

        # TODO faster shutter but colors inacurate and maybe stream delayed
        #self.camera.exposure_mode = 'sports' #TODO find right one

        print("Initially starting up camera data processing....")
        self.start_processing()
    

    def restart_camera_processing(self):
        self.stop_processing()
        self.start_processing()

    def stop_processing(self):
        print("Stopping all recording (shadowplay, streaming,...)")
        try:
            self.camera.stop_recording(splitter_port=0) # data collection photos
        except (PiCameraNotRecording, BrokenPipeError):
            pass
        try:
            self.camera.stop_recording(splitter_port=1) # shadowplay
        except (PiCameraNotRecording, BrokenPipeError):
            pass
        try:
            self.camera.stop_recording(splitter_port=2) # streaming
        except (PiCameraNotRecording, BrokenPipeError):
            pass
        if self.stream_runner_p is not None:
            # thanks to https://github.com/kkroening/ffmpeg-python/issues/162#issuecomment-571820244
            # self.stream_runner_p.communicate(str.encode("q")) #Equivalent to send a Q
            # time.sleep(10) 
            self.stream_runner_p.terminate()
            self.stream_runner_p = None

        self.any_video_running = False

    def start_processing(self):
        self.start_circular_record()
        self.start_streams()


    def start_circular_record(self):
        if self.feature_states.get_SHADOWPLAY():
            self.any_video_running = True
            print("Shadowplay activated to start process for that...")
            self.circular_buffer = start_buffer_recording(self.camera, self.camera_configuration.get_bitrate(), self.camera_configuration.get_shadowplay_time())

    def start_streams(self):
        # base source of video of camera
        # video was too late and after audio
        # fixed via nobuffer making video earlier https://stackoverflow.com/a/49273163
        source = ffmpeg.input('pipe:', format='h264', **{'r': self.camera_configuration.get_framerate(), 'thread_queue_size': 20480,  'fflags': 'nobuffer'})  

        audio = None
        if self.feature_states.get_STREAMING()[1]:
            # mic should be active
            # using nobuffer for same low latency as video
            # then applying async methods as in https://lzone.de/blog/Easily-fix-async-video-with-ffmpeg to sync audio to video
            audio = ffmpeg.input(self.camera_configuration.get_mic_input(), format='alsa', **{'ac': 1,"c:a": "pcm_s24le", "sample_rate": 192000, 'thread_queue_size': 20480, 'fflags': 'nobuffer', 'async': 1}) # reduce latency with no buffer then sync to video via async 1 # not needed and inacurate because changes 'itsoffset': MIC_OFFSET
        elif self.feature_states.get_STREAMING()[2]:
            # radio should be active    
            audio = ffmpeg.input(self.camera_configuration.get_radio_url(), **{'ac': 2, 'itsoffset': RADIO_OFFSET , 'thread_queue_size': 20480})
        
        # only video no audio to ml stream
        if audio is not None:
            ml_output_stream = ffmpeg.output(source, audio, self.camera_configuration.get_object_recognition_stream_url(), format='rtsp',
                **{
                    'fflags': 'nobuffer',
                    'threads': 2,
                    # copy of normal streaming audio output
                    'acodec': 'aac', 'ac': 1, 'ar': 44100, 'ab': '128k', 'af': 'highpass=200,lowpass=2100,volume=4,loudnorm',
                    'vcodec':'copy',
                    'reconnect': 1,'reconnect_at_eof': 1, 'reconnect_streamed': 1, 'reconnect_delay_max': 30 
                }
            )
        else:
            ml_output_stream = ffmpeg.output(source, self.camera_configuration.get_object_recognition_stream_url(), format='rtsp',
                **{
                    'fflags': 'nobuffer',
                    'threads': 2,
                    'vcodec':'copy',
                    'reconnect': 1,'reconnect_at_eof': 1, 'reconnect_streamed': 1, 'reconnect_delay_max': 30
                }
            )

        stream_url = self.camera_configuration.get_stream_url()

        if audio is not None:
            # see these for audio implementation details since docs suck
            # https://github.com/kkroening/ffmpeg-python/issues/26
            # https://github.com/kkroening/ffmpeg-python/pull/45#issue-159702983
            streaming_output = ffmpeg.output(source, audio, stream_url, format='flv',
                **{
                    'threads': 3,
                    # audio high low filter here to reduce usb mic noise floor, then boost then normalize audio too
                    # afftdn noise reduction filter seems to be problem and too much making stream unstable  # ,afftdn
                    'acodec': 'aac', 'ac': 1, 'ar': 44100, 'ab': '128k', 'af': 'highpass=200,lowpass=2100,volume=4,loudnorm', 
                    'vcodec':'copy',
                    'reconnect': 1,'reconnect_at_eof': 1, 'reconnect_streamed': 1, 'reconnect_delay_max': 30 
                }
            )
        else:
            streaming_output = ffmpeg.output(source, stream_url, format='flv',
                **{
                    'threads': 3,
                    # -acodec aac -ac 2 -ar 44100 -ab 128k
                    'vcodec':'copy',
                    'reconnect': 1,'reconnect_at_eof': 1, 'reconnect_streamed': 1, 'reconnect_delay_max': 30 
                }
            )

        stream = None
        if self.feature_states.get_OBJECT_DETECTION_STREAMING() and self.feature_states.get_STREAMING()[0]:
            # use almost recommmended way but not splititng and reencoding but merging output copy directly
            stream = ffmpeg.merge_outputs(streaming_output, ml_output_stream)
        elif self.feature_states.get_STREAMING()[0]:
            stream = streaming_output
        elif self.feature_states.get_OBJECT_DETECTION_STREAMING():
            stream = ml_output_stream

        if stream is not None:
            self.any_video_running = True
            self.stream_runner_p = stream.run_async(pipe_stdin=True)
            print("Starting pushing frames from camera into ffmpeg stream stdin...")
            self.camera.start_recording(self.stream_runner_p.stdin, format='h264', bitrate=self.camera_configuration.get_bitrate(), splitter_port=2) #splitter port to also circular record at same time
        else:
            pass
            # print("No streaming active...neither object detection nor online streaming...")

    def data_collection_call(self):
        if self.feature_states.get_DATA_COLLECTION():
            check_make_photo(self.camera, self.any_video_running)


def camera_manager_loop(feature_states: FeatureStates, camera_configuration: CameraConfiguration):
    print("Initializing camera manager....")
    camera_managment = CameraManagment(feature_states, camera_configuration)

    print("Starting loop to wait and check if any features were changed...")
    while True:
        # re-start recording if modes changes to account for activated/deactivated features
        if feature_states.did_features_change():
            feature_states.set_features_changed(False)
            camera_managment.restart_camera_processing()
 
        # handle requests to save shadowplay from buffer onto disk
        if feature_states.get_shadowplay_request():
            print("Save request received saving clip locally now...")
            feature_states.set_shadowplay_request(False)
            save_local_buffer(camera_managment.camera, camera_managment.circular_buffer)

        # also call this every loop to check if photo should be make if data collection is on
        camera_managment.data_collection_call()

        #stop process from keeping cpu busy
        time.sleep(1)
