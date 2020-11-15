# TODO config 
# if internet radio enabled and which
# if mic is enabled

class FeatureStates:
    def __init__(self):
        self.OBJECT_DETECTION_STREAMING = True # default off for network and resource reasons
        self.DATA_COLLECTION = False # default is off because almost never needed

        self.STREAMING = False # default start with off for privacy and network reasons
        self.STREAMING_mic = False
        self.STREAMING_radio = True

        self.SHADOWPLAY = False
        self.shadowplay_request = False

        self.changed_features = False

    # Have to use getters and setters here because it's used in a multiprocessing manager and this does not allow direct access

    ####### Feature changes marker #######

    def did_features_change(self):
        return self.changed_features

    def set_features_changed(self, value: bool):
        self.changed_features = value

    ####### shadowplay #######
    def get_SHADOWPLAY(self):
        return self.SHADOWPLAY

    def set_SHADOWPLAY(self, value: bool):
        self.SHADOWPLAY = value
        self.changed_features = True

    def get_shadowplay_request(self):
        return self.shadowplay_request

    def set_shadowplay_request(self, value: bool):
        self.shadowplay_request = value

    ####### object detection #######
    def get_OBJECT_DETECTION_STREAMING(self):
        return self.OBJECT_DETECTION_STREAMING

    def set_OBJECT_DETECTION_STREAMING(self, value: bool):
        self.OBJECT_DETECTION_STREAMING = value
        self.changed_features = True

    ####### Streaming #######
    def get_STREAMING(self):
        return self.STREAMING, self.STREAMING_mic, self.STREAMING_radio

    def set_STREAMING(self, state: bool, mic: bool, radio: bool):
        self.STREAMING = state
        self.STREAMING_mic = mic
        self.STREAMING_radio = radio
        self.changed_features = True

    ####### Data collection #######
    def get_DATA_COLLECTION(self):
        return self.DATA_COLLECTION

    def set_DATA_COLLECTION(self, value: bool):
        self.DATA_COLLECTION = value
        self.changed_features = True
