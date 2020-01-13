import time
import socket
from threading import Thread
from application.stream.RootStream import RootStream
import resources.settings


class CameraController(Thread):
    """
    Initialize a 1:1 RootStream to every Camera from the CSV File.
    Manages client requests and instantiates dynamically on request streams.
    """
    def __init__(self, ip):
        super().__init__()
        self.cameraip = ip
        self.cameraport = 554
        self.buffersize = 1024
        self.playreceived = False
        self.rootstreampath = 'rtsp://' + ip + ':554/MediaInput/h264/stream_1'

        self.rootstream = RootStream(src=self.rootstreampath).start()
        if self.rootstream.ret:
            print("--- Successfully connected to Camera({}) ---\n".format(ip))
        else:
            print("--- Can't connect to Camera({}) ---\n".format(ip))

        self.camerasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camerasocket.connect((self.cameraip, self.cameraport))
        resources.settings.rootRetDict[self.cameraip] = self.rootstream.ret    # Set global ret in settings.py class

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
            resources.settings.rootFrameDict[self.cameraip] = self.rootstream.read()
