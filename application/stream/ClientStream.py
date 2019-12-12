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
    def __init__(self, settings, clientaddress):
        super().__init__()
        print("__init__(ClientStream settings):", settings)
        print("__init__(ClientStream address):", clientaddress)
        self.cameraIp = settings[0]
        self.settings = settings
        self.clientAddress = clientaddress
        self.compressionRate = 70

        # Create a TCP Socket
        # self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Create a UDP Socket
        self.clientSocketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Image compression function. Default value for compression: 70
        self.encode_param = [int(cv2.IMWRITE_EXR_TYPE_HALF), self.compressionRate]
        """
        # Trys to connect Stream and Device Socket
        self.connectStatus = self.tryToConnect()
        if self.connectStatus:
        # Sending with TCP
            self.sendToDevice()
        """
        # Sending with UDP
        self.sendToDevice()

    # Only important for TCP
    """
    def tryToConnect(self):
        # Trys to connect ClientStream Socket with Client Device Socket
        try:
            self.clientSocket.connect(self.clientAddress)
            print("ClientSocket:" + str(self.clientAddress) + " connected.")
            return True
        except ConnectionError as ce:
            print(ce)
            print("ClientSocket:" + str(self.clientAddress) + "connection failed.")
            return False
    """


    def sendToDevice(self):
        """
        Sends (converted) Frame from RootStream via Socket to the Socket on the device
        """
        while True:
            if resources.settings.rootRetDict[self.cameraIp]:
                clientFrame = resources.settings.rootFrameDict[self.cameraIp]

                # if there are no settings, the server will stream the H.264 frame to the client
                if self.settings:
                    ip, codec, fps, width, height = self.settings

                    # - insert openCV convert functions here -
                    # Function to resize the frame
                    clientFrame = cv2.resize(src=clientFrame, dsize=(int(width), int(height)),
                                             interpolation=cv2.INTER_LINEAR)
                    # Function to set the format of the frame
                    result, clientFrame = cv2.imencode('.jpg', clientFrame, self.encode_param)

                data = pickle.dumps(clientFrame, 0)
                size = len(data)

                # TCP
                # Socket sending to client
                # self.clientSocket.sendall(struct.pack(">L", size) + data)

                # UDP
                """
                ***************
                -- Important --
                ***************
                
                To run UDP on Mac, you need to set the maximum UDP-package (65.535 bytes).
                Run on terminal:                
                ******************************************
                sudo sysctl -w net.inet.udp.maxdgram=65535
                ******************************************
                """
                # Socket sending to client
                if size < 65535:
                    self.clientSocketUDP.sendto(struct.pack(">L", size) + data, self.clientAddress)
                else:
                    print("Data size too big for UDP -> Size:", size)
                    self.compressionRate -= 1
                    self.encode_param = [int(cv2.IMWRITE_EXR_TYPE_HALF), self.compressionRate]
                    print("New compressionRate Value:", self.compressionRate)
