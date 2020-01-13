import base64
import socket
import pickle
import struct
import cv2
import sys
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
        self.camip = camip
        self.clientaddress = clientaddress
        # self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpsocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def run(self):
        """
        Sends (converted) Frame from RootStream via Socket to the Socket on the device
        """
        print("Clientstream trying to stream to:", self.clientaddress)
        # self.clientsocket.connect(self.clientaddress)
        print("### Connected to: " + str(self.clientaddress))
        while True:
            if resources.settings.rootRetDict[self.camip]:
                clientframe = resources.settings.rootFrameDict[self.camip]
                frame = cv2.resize(clientframe, (50, 50))  # resize the frame
                encoded, buffer = cv2.imencode('.jpeg', frame)
                jpg_as_text = base64.b64encode(buffer)
                self.udpsocket.sendto(buffer, self.clientaddress)
                #print("### SENT " + str(self.clientaddress) + ": ###\n", frame)
