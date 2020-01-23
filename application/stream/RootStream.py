import time
from multiprocessing import Process
from threading import Thread

import cv2

# For face detection only:
cascPath = "haarcascade.xml"
faceCascade = cv2.CascadeClassifier(cascPath)


class RootStream(Thread):
    """
    1:1 RTSP Stream Connection from Server to Camera.

    """

    def __init__(self, src=0):
        super().__init__()
        self.src = src
        self.stream = None
        self.ret = None
        self.frame = None
        self.connected = False
        self.attempts = 1

        self.initstream()

    def resetattempts(self):
        """
        Reset self.attempts to 1.

        """
        return 1

    def initstream(self):
        """
        Initialize the 1:1 Stream from the server to the camera.

        """
        self.stream = cv2.VideoCapture(self.src)
        self.ret, self.frame = self.stream.read()
        if self.ret:
            print("--- Successfully connected to Camera({}) ---".format(self.src))
        else:
            self.reconnectstream()

    def reconnectstream(self):
        """
        Trys to reconnect to the camera, if the connection is lost.

        """
        print("--- Can't connect to Camera({}) ---\n".format(self.src))
        while True:
            print("--- Reconnecting... ---".format(self.src))
            print('--- Attempts: {} ---'.format(self.attempts))
            self.attempts += 1
            self.stream.release()
            self.stream = cv2.VideoCapture(self.src)
            self.ret, self.frame = self.stream.read()
            if self.ret:
                print("--- Successfully reconnected. ---".format(self.src))
                print('--- Attempts needed: {} ---'.format(self.attempts))
                self.attempts = self.resetattempts()
                break
            else:
                time.sleep(0.2)
                continue

    def read(self):
        """
        Returns the frame from the camera stream, if ret is true.

        """
        if self.ret:
            self.connected = True
            return self.ret, self.frame
        else:
            self.connected = False
            return None

    def run(self):
        """
        Start infinite loop which reads the ret and frame from the camera,
        until the thread is stopped.

        """
        while True:
            self.ret, self.frame = self.stream.read()
            """
            --- Following Code is for Facerecognition only, delete after use ---
            
            """
            # gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            #
            # faces = faceCascade.detectMultiScale(
            #     gray,
            #     scaleFactor=1.1,
            #     minNeighbors=5,
            #     minSize=(30, 30),
            #     flags=cv2.CASCADE_SCALE_IMAGE
            # )
            #
            # #  Draw a rectangle around the faces
            # for (x, y, w, h) in faces:
            #      cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if not self.ret:
                self.reconnectstream()
                continue
