import socket
from threading import Thread
import re
from application.stream.ClientStream import ClientStream
import gi
gi.require_version('Gst', '1.0')
# from gi.repository import GObject, Gst, GstVideo, GstRtspServer
BUFFERSIZE = 1024
PLAYSTATUS = False


class Client(Thread):
    def __init__(self, serveraddress, cameracontroller):
        super().__init__()
        self.connection = None
        self.clientaddress = None
        self.clientstream = None
        self.receivedplay = False
        self.serveraddress = serveraddress
        self.cameracontroller = cameracontroller
        self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.request = {}

    def createclientstream(self, clientaddress):
        """
        Create a threaded ClientStream
        """
        self.clientstream = ClientStream(self.cameracontroller.cameraip, clientaddress)
        return True

    def handlerequest(self, input, clientaddress):
        """
        Analyze Request from Client and then calculate and send response
        """
        global PLAYSTATUS
        data = input.decode()
        lines = data.split("\n")
        self.request['method'] = lines[0].split()[0]

        if self.request['method'] == "DESCRIBE" or self.request['method'] == "OPTIONS":
            print("+++ Method " + self.request['method'] + " triggered +++")
            data = data.replace(self.serveraddress[0]+":"+str(self.serveraddress[1]),
                              self.cameracontroller.cameraip + ":"
                              + str(self.cameracontroller.cameraport) + "/MediaInput/h264/stream_1/")

        elif self.request['method'] == "SETUP":

            ip = clientaddress[0]
            line0 = lines[0]
            line3 = lines[3]
            line4 = lines[4]
            self.request["url"] = line0.split()[1]
            self.request["transport"] = line3.split()[1]
            try:
                self.request["session"] = line4.split()[1]
            except IndexError as ie:
                print(ie)
                pass
            video = "trackID=1"
            audio = "trackID=2"

            if re.search(video, self.request["url"]):
                if re.search("client_port", self.request["transport"]):
                    self.request["clientportsV"] = str(self.request["transport"].split(";")[-1].split("=")[1])
                    self.createclientstream((ip, int(self.request["clientportsV"].split("-")[0])))
                    print("+++ CLIENTSTREAM CREATED +++")

            elif re.search(audio, self.request["url"]):
                if re.search("client_port", self.request["transport"]):
                    self.request["clientportsA"] = str(self.request["transport"].split(";")[-1].split("=")[1])

        elif self.request['method'] == "PLAY":
            line1 = lines[1]
            print("+++ Method " + self.request['method'] + " triggered +++")
            self.request["cseq"] = line1.split()[1]
            response = self.sendok()
            print(response)
            print('### CLIENT: ###\n' + data + "\n")
            print('### RESPONSE: ###\n' + response + "\n")
            # self.clientstream.start()
            PLAYSTATUS = True
            return response

        print('### CLIENT: ###\n' + data + "\n")
        response = self.cameracontroller.sendToCamera(data)
        if self.request['method'] == "SETUP":
            if re.search("server_port", response):
                response = re.sub(r'\bserver_port=\d*-\d*',
                       "server_port="+str(self.serveraddress[1])+"-"+str(self.serveraddress[1]+1),
                       response)
        print('### RESPONSE: ###\n' + response + "\n")
        return response

    def sendok(self):
        cseq = self.request["cseq"]
        session = self.request["session"]
        response = 'RTSP/1.0 200 OK\r\nCSeq: '+cseq+'\r\nConnection: Keep-Alive\r\nSession: '+session+'\r\n\r\n'
        return response

    def run(self):
        global PLAYSTATUS
        self.tcpsocket.bind(self.serveraddress)
        self.tcpsocket.listen(1)
        self.connection, self.clientaddress = self.tcpsocket.accept()
        print("### CLIENT-THREAD STARTED" + str(self.clientaddress) + " ###")

        try:
            while True:
                data = self.connection.recv(BUFFERSIZE)
                self.receivedplay = True
                if data:
                    answer = self.handlerequest(data, self.clientaddress)
                    self.connection.send(answer.encode())
                    if PLAYSTATUS:
                        print('############################################################## PLAYSTATUS True || Start Stream')
                        self.clientstream.start()
                else:
                    print("No more data from:", self.clientaddress)
                    print("TCP server communication socket closed.\nStart streaming. ")
                    break
        finally:
            self.connection.close()
