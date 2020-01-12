import csv
import socket
from threading import Thread

from application.controller.CameraController import CameraController
from application.server.Client import Client

DEFAULT_SPECS = ["h264", "25", "1920", "1080"]
BUFFERSIZE = 1024


class Server(Thread):
    """
    Main Application
    Initialize a 1:1 RTSP Stream with every Camera listed in cameras.csv
    """
    def __init__(self, csv_path):
        super(Server, self).__init__()
        self.csv_path = csv_path
        self.server_address = ('192.168.0.248', 5502)
        self.csv_data = []
        self.cameraControllers = []
        self.clients = []

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
        print("### SERVER STARTED" + str(self.server_address) + " ###")
        client = Client(self.server_address, self.cameraControllers[0])
        print("\n### SERVER IS WAITING WITH EMPTY CLIENTSOCKET ###\n")
        client.start()
        print("\n### CLIENT STARTED ###\n")
        while True:
            if client.connected:
                self.clients.append(client)
                client = Client(self.server_address, self.cameraControllers[0])


