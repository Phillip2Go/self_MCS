import csv
import time
from threading import Thread
from application.controller.CameraController import CameraController
from application.stream.RtspStream import RtspStreamer

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
        self.cameracontrollers.append(CameraController())
        for cam in self.csv_data:
            if len(cam) is 1:
                ip = cam[0]
                self.cameracontrollers.append(CameraController(ip))

            elif len(cam) is 3:
                ip, username, password = cam
                self.cameracontrollers.append(CameraController(ip))

    def startcameras(self):
        """
        Start up all Cameras and connect to RootStream
        """
        for cam in self.cameracontrollers:
            cam.start()

    def run(self):
        """
        Creates a RTSP-Socket for every Client
        """
        rtspsocket1 = RtspStreamer(None, "open", 554)
        time.sleep(0.5)
        rtspsocket1.start()
        """
        rtspsocket2 = RtspStreamer("open1", 8555, "rtsp://192.168.0.11:554/mediainput/h264/stream_1")
        rtspsocket3 = RtspStreamer("open1", 8556, "rtsp://192.168.0.11:554/mediainput/h264/stream_1")
        rtspsocket4 = RtspStreamer("open1", 8557, "rtsp://192.168.0.11:554/mediainput/h264/stream_1")
        rtspsocket5 = RtspStreamer("open1", 8558, "rtsp://192.168.0.11:554/mediainput/h264/stream_1")
        rtspsocket6 = RtspStreamer("open1", 8559, "rtsp://192.168.0.11:554/mediainput/h264/stream_1")

        
        time.sleep(0.5)
        rtspsocket2.start()
        time.sleep(0.5)
        rtspsocket3.start()
        time.sleep(0.5)
        rtspsocket4.start()
        time.sleep(0.5)
        rtspsocket5.start()
        time.sleep(0.5)
        rtspsocket6.start()
        time.sleep(0.5)
        """
