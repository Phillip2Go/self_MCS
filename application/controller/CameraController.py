import time

from threading import Thread
from application.stream.RootStream import RootStream
from application.stream.ClientStream import ClientStream

import resources.settings
resources.settings.rootRet = False
resources.settings.rootFrame = None


class CameraController(Thread):
    """
    Initialize a 1:1 RootStream to every Camera from the CSV File.
    Manages client requests and instantiates dynamically on request streams.
    """
    def __init__(self, ip):
        super().__init__()
        self.cameraIp = ip
        self.rootStreamPath = 'rtsp://' + ip + ':554/MediaInput/h264/stream_1'
        self.rootStream = RootStream(src=self.rootStreamPath).start()
        print("RootStream connected to Cam(ip):", ip)
        resources.settings.rootRet = self.rootStream.ret    # Set global ret in settings.py class
        self.clientStreams = []
        time.sleep(1)

    def createClientStream(self, settings, clientAddress):
        """
        Create a threaded ClientStream and append the stream to the self.clientStream List
        """
        cs = Thread(target=ClientStream, args=(settings, clientAddress))
        cs.start()
        self.clientStreams.append(cs)
        return True

    def run(self):
        """
        Set the actual RootStream frame to resources.settings.rootRet -> Global
        """
        while True:
            resources.settings.rootFrameDict[self.cameraIp] = self.rootStream.read()
