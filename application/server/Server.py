import csv
from threading import Thread

from application.controller.CameraController import CameraController
from application.server.Client import Client
import sys

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
        self.server_address = (sys.argv[1], 5502)
        self.csv_data = []
        self.cameracontrollers = []
        self.clients = []

        # Starting up all methods:
        self.readcsv()
        self.initcameras()
        self.startcameras()

    def readcsv(self):
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

    def initcameras(self):
        """
        Initialize for every camera a CameraController with connect to RootStream
        """
        for cam in self.csv_data:
            if len(cam) is 1:
                ip = cam[0]
                self.cameracontrollers.append(CameraController(ip))

            elif len(cam) is 3:
                ip, username, password = cam
                pass

    def startcameras(self):
        """
        Start up all Cameras and connect to RootStream
        """
        for cam in self.cameracontrollers:
            cam.start()

    def run(self):
        """
        Creating a receive Socket to listen to the client.
        """
        print("### SERVER STARTED" + str(self.server_address) + " ###")
        client = Client(self.server_address, self.cameracontrollers[0])
        print("\n### SERVER IS WAITING WITH EMPTY CLIENTSOCKET ###\n")
        client.start()
        print("\n### CLIENT STARTED ###\n")
        while True:
            if client.receivedplay:
                client.tcpsocket.close()
                # client = Client(self.server_address, self.cameracontrollers[0])
                # client.start()
                # print("\n### NEW CLIENT STARTED ###\n")



