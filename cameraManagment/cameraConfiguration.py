class CameraConfiguration:
    def __init__(self, stream_ingest_url: str, stream_key: str, ml_stream_url: str, mic_input: str, radio_url: str):
        self.stream_ingest_url = stream_ingest_url
        self.stream_key = stream_key
        self.ml_stream_url = ml_stream_url

        # if you change bitrate shadowplay will be off more because divier down there is wrong
        self.shadowplay_time = 50
        # working with double stream as far as I see
        #BITRATE = 2500000

        self.bitrate = 2800000
        #self.resolution_width = 1920
        #self.resolution_height = 1080
        self.framerate = 30

        #self.bitrate = 3500000
        #self.bitrate = 1400000
        self.resolution_width = 1280
        self.resolution_height = 720
        #self.framerate = 60

        self.mic_input = mic_input
        self.radio_url = radio_url

    def get_stream_url(self):
        return self.stream_ingest_url + self.stream_key

    def get_object_recognition_stream_url(self):
        return self.ml_stream_url

    def get_shadowplay_time(self):
        return self.shadowplay_time

    def get_bitrate(self):
        return self.bitrate

    def get_resolution(self):
        return (self.resolution_width, self.resolution_height)

    def get_framerate(self):
        return self.framerate

    def get_mic_input(self):
        return self.mic_input

    def get_radio_url(self):
        return self.radio_url
