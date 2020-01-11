import socket

OWN_IP = '192.168.0.248'
OWN_TCP_PORT = 5005

CAMERA_IP = '192.168.0.11'
CAMERA_PORT = 554

BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

if __name__ == "__main__":
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.bind((OWN_IP, OWN_TCP_PORT))
    clientsocket.listen(1)

    camerasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    camerasocket.connect((CAMERA_IP, CAMERA_PORT))

    conn, addr = clientsocket.accept()
    print('Connection address:', addr)
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        print("CRESTRON( -> Camera):", data)
        camerasocket.send(data)
        data = camerasocket.recv(BUFFER_SIZE)
        print("CAMERA( -> Crestron):", data)
        conn.send(data)
    conn.close()
    camerasocket.close()