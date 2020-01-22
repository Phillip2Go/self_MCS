import csv
import subprocess
import time
from threading import Thread
import socket
from application.controller.CameraController import CameraController
from application.stream.RtspStream import RtspStreamer

RTSP_STREAMS = [("192.168.0.11", "stream", 8555),
                ("192.168.0.11", "stream", 8556)]


class Server(Thread):
    """
    Main Server Thread.
    Responsible for initializing a CameraController and their RootStreams for every
    Camera-Ip in the CSV-File. Also initializes the RtspStreams.
    """
    def __init__(self, csv_path):
        super(Server, self).__init__()
        self.csv_path = csv_path
        self.csv_data = []
        self.cameracontrollers = []
        self.rtspstreams = []
        self.readcsv()
        self.initcameras()
        self.startcameras()
        self.initrtspstreams(RTSP_STREAMS)
        self.startrtspstreams()
        time.sleep(1)
        # self.startproxyservers()
        # self.ip = socket.gethostbyname(socket.gethostname())

    def readcsv(self):
        """ Reads the .csv in project directory """
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
        """ Initializes a CameraController for each Camera"""
        for cam in self.csv_data:
            if len(cam) is 1:
                ip = cam[0]
                self.cameracontrollers.append(CameraController(ip))
            elif len(cam) is 3:
                ip, username, password = cam
                self.cameracontrollers.append(CameraController(ip))

    def startcameras(self):
        """ Start all CameraController-Threads """
        for cam in self.cameracontrollers:
            cam.start()


    def initrtspstreams(self, settings):
        for settingstuple in settings:
            stream = RtspStreamer(settingstuple[0], settingstuple[1], settingstuple[2])
            self.rtspstreams.append(stream)

    def startrtspstreams(self):
        for stream in self.rtspstreams:
            stream.start()
            time.sleep(0.2)

    def startproxyservers(self):
        if len(self.rtspstreams) is 1:
            stream = self.rtspstreams[0]
            args = ["live555ProxyServer", "rtsp://localhost:" + str(stream.port) + "/" + stream.name]
            s = subprocess.Popen(args=args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            print("--- Proxsyerver for {} initialized under following URL: rtsp://127.0.0.1/stream ---".format(stream.camerakey))
        else:
            i = 1
            args = ["live555ProxyServer"]
            for stream in self.rtspstreams:
                args.append("rtsp://localhost:" + str(stream.port) + "/" + stream.name)
                print("--- Proxsyerver for {} initialized under following URL: rtsp://127.0.0.1}/stream_{} ---".format(
                    stream.camerakey, i, self.ip))
                i = i + 1
            s = subprocess.Popen(args=args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def run(self):
        while True:
            for camera in self.cameracontrollers:
                if not camera.rootstream:
                    time.sleep(1)
                    self.startproxyservers()
