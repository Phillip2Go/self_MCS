import sys
import socket
import struct
import pickle
import cv2

UDP_IP = '127.0.0.1'
UDP_PORT = int(sys.argv[1])
SERVER_ADDRESS = ('localhost', 5500)
SETTINGS = str(UDP_PORT) + "," + sys.argv[2] + ",mjpeg,15,640,360"


if __name__ == '__main__':
    # TCP server socket for communication
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(SERVER_ADDRESS)
    try:
        server_socket.sendall(SETTINGS.encode())
        print("Successfully send settings to server.")
    finally:
        print('Closing TCP Socket. Start Stream Socket.')
        server_socket.close()

    # UDP receive socket for frames
    udpRecv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpRecv_socket.bind((UDP_IP, UDP_PORT))
    print("Receive Socket created for UDP_PORT:", UDP_PORT)

    data = b""
    payload_size = struct.calcsize(">L")
    print("payload_size: {}".format(payload_size))

    while True:
        data, address = udpRecv_socket.recvfrom(65535)
        # print("DATA :", data)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        while len(data) < msg_size:
            data = udpRecv_socket.recvfrom(65535)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow("UDP Client: " + sys.argv[2], frame)
        cv2.waitKey(1)
