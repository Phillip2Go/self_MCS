import csv
import socket
from threading import Thread

from application.controller.CameraController import CameraController

DEFAULT_SPECS = ["h264", "25", "1920", "1080"]


class Server(Thread):
    """
    Main Application
    Initialize a 1:1 RTSP Stream with every Camera listed in cameras.csv
    """
    def __init__(self, csv_path):
        super(Server, self).__init__()
        self.csv_path = csv_path
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 5500)
        self.csv_data = []
        self.cameraControllers = []

        # Starting up all methods:
        self.readCsv()
        self.initCameras()
        self.startCameras()

    def readCsv(self):
        """
        Reading the CSV file
        """
        with open(self.csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    self.csv_data.append(row)
                    line_count += 1

    def initCameras(self):
        """
        Initialize for every camera a CameraController with connect to RootStream
        """
        for cam in self.csv_data:
            if len(cam) is 1:
                ip = cam[0]
                self.cameraControllers.append(CameraController(ip))

            elif len(cam) is 3:
                ip, username, password = cam
                pass

    def startCameras(self):
        """
        Start up all Cameras and connect to RootStream
        """
        for cam in self.cameraControllers:
            cam.start()

    def run(self):
        """
        Creating a receive Socket to listen to the client.
        """
        print('Server starting up on - {} Port: {}'.format(*self.server_address))
        self.recvSocket.bind(self.server_address)
        self.recvSocket.listen(1)
        while True:
            print("\nWaiting for a connection...\n")
            connection, client_address = self.recvSocket.accept()
            try:
                print("Connection to client:", client_address)
                while True:
                    data = connection.recv(128)
                    print('Received data from client: {!r}'.format(data))
                    if data:
                        self.handleRequest(data, client_address)
                    else:
                        print("No more data from:", client_address)
                        print("TCP server communication socket closed.\nStart streaming. ")
                        break
            finally:
                connection.close()

    def handleRequest(self, line, clientAddress):
        """
        Wait for clients who connect to the receive socket from Server.
        After a client connect, the Server creates with the CameraController a new ClientStream.
        The ClientStream will send (converted) frames to the socket from the device.
        """
        ca = clientAddress[0], int(line.decode().split(",")[0])
        settings = line.decode().split(",")[1:]
        print("Frames sending to Client:", ca)
        self.cameraControllers[0].createClientStream(settings, ca)
        return True
