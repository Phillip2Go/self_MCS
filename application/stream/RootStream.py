import cv2
import time
from threading import Thread


class RootStream:
    """
    1:1 RTSP Stream Connection from Server to Camera
    """
    def __init__(self, src=0):
        # Initialize the stream from the camera via cv2
        self.src = src
        self.stream = cv2.VideoCapture(self.src)
        # Read the first frame from the camera stream
        (self.ret, self.frame) = self.stream.read()
        # Initialize the var used to indificate if the thread should be stopped
        self.stopped = False

    def start(self):
        """
        Start the thread to read ret/frame from the camera stream
        """
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        """
        Start infinite loop until the thread is stopped
        """
        while True:
            # if thread indicator var is set, stop the thread
            if self.stopped:
                return
            # else, read next ret/frame from the stream
            (self.ret, self.frame) = self.stream.read()
            # if self.ret is False, the RootStream trys to reconnect the CameraStream
            if not self.ret:
                print("RootStream connection lost, trys to reconnect..")
                st = time.time()
                cap = cv2.VideoCapture(self.src)
                print("Time needed to reconnect: ", time.time() - st)
                continue

    def read(self):
        """
        Return the frame from the camera stream
        """
        return self.frame

    def stop(self):
        """
        Indicate that the thread should stop
        """
        self.stopped = True
