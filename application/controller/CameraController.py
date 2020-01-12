import time
import socket
from threading import Thread
from application.stream.RootStream import RootStream
from application.stream.ClientStream import ClientStream

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
            print("Successfully retrieving Stream from " + ip)
        else:
            print("Couldn't get Stream from " + ip)

        self.camerasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camerasocket.connect((self.cameraip, self.CAMERAPORT))

        resources.settings.rootRetDict[self.cameraip] = self.rootstream.ret    # Set global ret in settings.py class
        self.clientstreams = []
        time.sleep(1)

    def sendToCamera(self, message):
        """
        Sends a String via TCP to the RTSP Port of the Camera
        (Used for RTSP-SETUP)
        """
        self.camerasocket.send(message)
        data = self.camerasocket.recv(self.BUFFERSIZE)
        return data


    def createClientStream(self, clientaddress):
        """
        Create a threaded ClientStream and append the stream to the self.clientStream List
        """
        cs = ClientStream(self.cameraip, clientaddress)
        self.clientstreams.append(cs)
        return True

    def run(self):
        """
        Set the actual RootStream frame to resources.settings.rootRet -> Global
        """
        while True:
            resources.settings.rootFrameDict[self.cameraip] = self.rootstream.read()
