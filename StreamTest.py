import cv2
from application.stream.RootStream import RootStream

PATH = 'rtsp://192.168.22.11:554/MediaInput/h264/stream_1'
cap = RootStream(src=PATH).start()

while True:
    frame = cap.read()
    cv2.imshow(PATH, frame)

    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.stop()
