import sys
import socket
import struct
import pickle
import cv2

TCP_IP = '127.0.0.1'
TCP_PORT = int(sys.argv[1])
SERVER_ADDRESS = ('localhost', 5500)
SETTINGS = str(TCP_PORT) + "," + sys.argv[2] + ",mjpeg,15,640,360"


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

    # TCP receive socket for frames
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_socket.bind((TCP_IP, TCP_PORT))
    recv_socket.listen(10)
    print("Receive Socket created for TCP_PORT:", TCP_PORT)

    connection, address = recv_socket.accept()
    print("(Stream) - Receive Socket accepted.")

    data = b""
    payload_size = struct.calcsize(">L")
    print("payload_size: {}".format(payload_size))

    while True:
        # print("Recv: {}".format(len(data)))
        data += connection.recv(4096)

        # print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        # print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            data += connection.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow("TCP Client:" + sys.argv[2], frame)
        cv2.waitKey(1)
