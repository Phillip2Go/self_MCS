import socket
import pickle
import struct
import cv2
from threading import Thread

"""

-- Important --

To run UDP on Mac, you need to set the maximum UDP-package (65.535 bytes).
Run on terminal:   
             
    sudo sysctl -w net.inet.udp.maxdgram=65535

"""
import resources.settings


class ClientStream(Thread):
    """
    Duplicate frames from the RootStream and route them to the Client Device
    """
    def __init__(self, camip, clientaddress):
        super().__init__()
        print("ClientStream address:", clientaddress)
        self.camip = camip
        self.clientaddress = clientaddress
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        """
        Sends (converted) Frame from RootStream via Socket to the Socket on the device
        """
        print("Connecting to: " + str(self.clientaddress))
        self.clientsocket.connect(self.clientaddress)
        while True:
            if resources.settings.rootRetDict[self.camip]:
                clientFrame = resources.settings.rootFrameDict[self.camip]
                self.clientsocket.sendall(clientFrame)