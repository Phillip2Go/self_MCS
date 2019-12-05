import socket
import pickle
import struct
import cv2
from threading import Thread

import resources.settings


class ClientStream(Thread):
    """
    Duplicate frames from the RootStream and route them to the Client Device
    """
    def __init__(self, settings, clientAddress):
        print("__init__(ClientStream settings):", settings)
        print("__init__(ClientStream address):", clientAddress)
        self.cameraIp = settings[0]
        self.settings = settings
        self.clientAddress = clientAddress

        # Create a TCP Socket
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Create a UDP Socket
        self.clientSocketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Testcode, später dynamisch
        self.encode_param = [int(cv2.IMWRITE_EXR_TYPE_HALF), 90]
        """
        # Trys to connect Stream and Device Socket
        self.connectStatus = self.tryToConnect()
        if self.connectStatus:
            self.sendToDevice()
        """
        self.sendToDevice()

    def tryToConnect(self):
        """
        Trys to connect ClientStream Socket with Client Device Socket
        """
        try:
            self.clientSocket.connect(self.clientAddress)
            print("ClientSocket:" + str(self.clientAddress) + " connected.")
            return True
        except ConnectionError as ce:
            print(ce)
            print("ClientSocket:" + str(self.clientAddress) + "connection failed.")
            return False

    def sendToDevice(self):
        """
        Sends (converted) Frame from RootStream via Socket to the Socket on the device
        """
        while True:
            if resources.settings.rootRet:
                clientFrame = resources.settings.rootFrameDict[self.cameraIp]

                # if there are no settings, the server will stream the H.264 frame to the client
                if self.settings:
                    ip, codec, fps, width, height = self.settings

                    # - insert openCV convert functions here -
                    # clientFrame = cv2.resize(clientFrame, (width, height), interpolation='linear')
                    result, clientFrame = cv2.imencode('.jpg', clientFrame, self.encode_param)

                data = pickle.dumps(clientFrame, 0)
                size = len(data)
                print("Size is:", size)
                # TCP client sending
                # self.clientSocket.sendall(struct.pack(">L", size) + data)
                # UDP client sending
                self.clientSocketUDP.sendto(struct.pack(">L", size) + data, self.clientAddress)