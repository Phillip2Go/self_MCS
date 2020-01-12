import csv
import socket
from threading import Thread

from application.controller.CameraController import CameraController

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
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('192.168.0.248', 5501)
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
        print("### SERVER STARTED" + str(self.server_address) + " ###")
        self.recvSocket.bind(self.server_address)
        self.recvSocket.listen(1)
        while True:
            print("\n### SERVER IS WAITING FOR CLIENT ###\n")
            connection, client_address = self.recvSocket.accept()
            try:
                print("### CLIENT CONNECTED" + str(client_address) + " ###")
                while True:
                    data = connection.recv(BUFFERSIZE)
                    if data:
                        answer = self.handleRequest(data, client_address)
                        connection.send(answer)

                    else:
                        print("No more data from:", client_address)
                        print("TCP server communication socket closed.\nStart streaming. ")
                        break
            finally:
                connection.close()

    def handleRequest(self, data, clientaddress):
        """
        Passthrough all the RTSP-Requests until Client sends DESCRIBE, SETUP  and finally PLAY Method
        Then create a Clientstream, which will handle sending the video
        """
        new = data.decode()
        method = new.split()[0]
        print("+++ Method " + method + " triggered +++")
        if method == "DESCRIBE" or "OPTIONS":
            new = new.replace(self.server_address[0]+":"+str(self.server_address[1]),
                              self.cameraControllers[0].cameraip + ":"
                              + str(self.cameraControllers[0].CAMERAPORT) + "/MediaInput/h264/stream_1")

        elif method == "SETUP":
            ip = clientaddress[0]
            # port = new.split()[9].split(";")[2].split("=")[1].split("-")[0]
            self.cameraControllers[0].createClientStream((ip, None))

        elif method == "PLAY":
            self.cameraControllers[0].clientstreams[0].start()


        print('### CLIENT: ###\n' + new + "\n")
        new = new.encode()
        response = self.cameraControllers[0].sendToCamera(new)
        print('### RESPONSE: ###\n' + response.decode() + "\n")
        # ca = clientaddress[0], int(data.decode().split(",")[0])
        # settings = data.decode().split(",")[1:]
        # print("Frames sending to Client:", ca)
        # self.cameraControllers[0].createClientStream(settings, ca)
        return response
