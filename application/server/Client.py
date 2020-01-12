import socket
from threading import Thread

BUFFERSIZE = 1024

class Client(Thread):
    def __init__(self, serveraddress, cameracontroller):
        super().__init__()
        self.connection = None
        self.client_address = None
        self.connected = False
        self.serveraddress = serveraddress
        self.cameracontroller = cameracontroller
        self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def handleRequest(self, data, clientaddress):
        """
        Passthrough all the RTSP-Requests until Client sends DESCRIBE, SETUP  and finally PLAY Method
        Then create a Clientstream, which will handle sending the video
        """
        new = data.decode()
        method = new.split()[0]
        print("+++ Method " + method + " triggered +++")
        if method == "DESCRIBE" or "OPTIONS":
            new = new.replace(self.serveraddress[0]+":"+str(self.serveraddress[1]),
                              self.cameracontroller.cameraip + ":"
                              + str(self.cameracontroller.CAMERAPORT) + "/MediaInput/h264/stream_1")

        elif method == "SETUP":
            ip = clientaddress[0]
            # port = new.split()[9].split(";")[2].split("=")[1].split("-")[0]
            # self.cameraControllers[0].createClientStream((ip, None))

        elif method == "PLAY":
            self.cameracontroller.clientstreams[0].start()

        print('### CLIENT: ###\n' + new + "\n")
        new = new.encode()
        response = self.cameracontroller.sendToCamera(new)
        print('### RESPONSE: ###\n' + response.decode() + "\n")
        # ca = clientaddress[0], int(data.decode().split(",")[0])
        # settings = data.decode().split(",")[1:]
        # print("Frames sending to Client:", ca)
        # self.cameraControllers[0].createClientStream(settings, ca)
        return response

    def run(self):
        self.tcpsocket.bind(self.serveraddress)
        self.tcpsocket.listen(1)
        self.connection, self.client_address = self.tcpsocket.accept()
        print("### CLIENT-THREAD STARTED" + str(self.client_address) + " ###")

        try:
            while True:
                data = self.connection.recv(BUFFERSIZE)
                self.connected = True
                if data:
                    answer = self.handleRequest(data, self.client_address)
                    self.connection.send(answer)
                else:
                    print("No more data from:", self.client_address)
                    print("TCP server communication socket closed.\nStart streaming. ")
                    break
        finally:
            self.connection.close()
