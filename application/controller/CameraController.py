import socket
from multiprocessing import Process
from threading import Thread

import resources.settings
from application.stream.RootStream import RootStream


class CameraController(Thread):
    """
    Initialize a 1:1 RootStream to every Camera from the CSV File.
    Manages client requests and instantiates dynamically on request streams.
    """

    def __init__(self, ip=None):
        super().__init__()
        if ip:
            self.cameraip = ip
            self.cameraport = 554
            self.buffersize = 1024
            # self.playreceived = False

            # --- CHANGE RTSP <-> HTTP ---
            # self.rootstreampath = 'rtsp://' + ip + ':554/MediaInput/h264/stream_1'
            self.rootstreampath = 'http://' + ip + '/cgi-bin/mjpeg?resolution=1920x1080&framerate=25&quality=1'

            self.camerasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.camerasocket.connect((self.cameraip, self.cameraport))
            self.rootstream = RootStream(src=self.rootstreampath)
        else:
            self.cameraip = 0
            self.rootstream = RootStream()
        self.rootstream.start()
        # resources.settings.rootRetDict[self.cameraip] = self.rootstream.ret    # Set global ret in settings.py class

    def sendToCamera(self, message):
        """
        Sends a String via TCP to the RTSP Port of the Camera
        (Used for RTSP-SETUP)
        """
        self.camerasocket.send(message.encode())
        data = self.camerasocket.recv(self.buffersize)
        return data.decode()

    def run(self):
        """
        Set the actual RootStream frame to resources.settings.rootRet -> Global
        """
        while True:
            try:
                resources.settings.rootFrameDict[self.cameraip] = self.rootstream.read()
            except Exception as e:
                pass
